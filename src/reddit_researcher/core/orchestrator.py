from __future__ import annotations

import json
import logging
import os
import random
import sys
import time
from collections.abc import Iterator

from reddit_researcher.apis.reddit.adapter import RedditSourceAdapter
from reddit_researcher.apis.supabase.adapter import SupabaseSinkAdapter
from reddit_researcher.config.config import AppConfig, generate_run_id, load_config
from reddit_researcher.core.ratelimit import RateLimiter, compute_backoff_seconds
from reddit_researcher.core.telemetry import Stopwatch, TelemetryRecorder
from reddit_researcher.core.normalizers import normalize_comment, normalize_post


def main(argv: list[str] | None = None) -> int:
    _configure_logging()
    logger = logging.getLogger("reddit_researcher.probe")
    _ = argv or sys.argv[1:]

    try:
        cfg: AppConfig = load_config("config.yaml")
    except FileNotFoundError as exc:
        print(str(exc))
        return 2

    run_id = generate_run_id()
    logger.info(
        "starting run %s subreddit=%s listing=%s N=%s K=%s repl_more=%s supabase=%s",
        run_id,
        cfg.probe.subreddit,
        cfg.probe.listing,
        cfg.probe.post_limit,
        cfg.probe.comment_sample,
        cfg.probe.comment_replace_more_limit,
        bool(cfg.supabase.enabled),
    )
    # Local file outputs disabled: no JSONL or report writes

    limiter = RateLimiter(cfg.probe.qpm_cap, burst_tokens=1)
    telem = TelemetryRecorder()
    started_at = time.time()

    # Build adapters
    source = RedditSourceAdapter(cfg)
    logger.info("reddit source ready")

    # Fetch posts
    logger.info(
        "fetching posts listing=%s subreddit=%s limit=%s",
        cfg.probe.listing,
        cfg.probe.subreddit,
        cfg.probe.post_limit,
    )
    posts_iter = source.iter_posts(
        subreddit=cfg.probe.subreddit,
        listing=cfg.probe.listing,
        time_filter=cfg.probe.time_filter,
        limit=cfg.probe.post_limit,
    )

    posts = []
    posts_batch: list[dict[str, object]] = []
    post_ids_for_run: list[str] = []
    for s in posts_iter:
        limiter.acquire()
        posts.append(s)
        norm = normalize_post(s)
        posts_batch.append(norm)
        post_id = norm.get("id")
        if isinstance(post_id, str):
            post_ids_for_run.append(post_id)

    # Choose K posts to expand comments (by num_comments desc)
    posts_sorted = sorted(posts, key=lambda x: getattr(x, "num_comments", 0), reverse=True)
    sample = posts_sorted[: cfg.probe.comment_sample]
    logger.info("fetched %d posts; sampling %d for comments", len(posts), len(sample))

    # Expand comments with basic retry/backoff
    rng = random.Random()
    comments_per_post: list[int] = []
    comment_ids_for_run: list[str] = []
    comments_batch: list[dict[str, object]] = []
    for s in sample:
        attempts = 0
        while True:
            try:
                logger.debug(
                    "expand comments submission_id=%s replace_more=%s",
                    getattr(s, "id", None),
                    cfg.probe.comment_replace_more_limit,
                )
                with Stopwatch() as sw:
                    comments = source.fetch_comments(
                        submission_id=getattr(s, "id", ""),
                        replace_more_limit=cfg.probe.comment_replace_more_limit,
                    )
                telem.record(
                    endpoint="comments.fetch",
                    headers={},
                    elapsed_s=sw.elapsed,
                )
                comments_per_post.append(len(comments))
                def _gen() -> Iterator[dict[str, object]]:
                    for c in comments:
                        nc = normalize_comment(c, link_id=getattr(s, "id", None))
                        cid = nc.get("id")
                        if isinstance(cid, str):
                            comment_ids_for_run.append(cid)
                        comments_batch.append(nc)
                        yield nc

                # Local comment JSONL writes disabled
                _ = list(_gen())
                break
            except Exception:
                attempts += 1
                delay = compute_backoff_seconds(attempts - 1, rng=rng)
                time.sleep(delay)
                if attempts >= 5:
                    break

    ended_at = time.time()

    comments_total = len(comments_batch)

    # Compute simple per-post stats for expanded posts
    def _percentile(sorted_vals: list[int], pct: float) -> int:
        if not sorted_vals:
            return 0
        k = max(0, min(len(sorted_vals) - 1, int(round((pct / 100.0) * (len(sorted_vals) - 1)))))
        return sorted_vals[k]

    cps_sorted = sorted(comments_per_post)
    per_post_stats = {
        "min": cps_sorted[0] if cps_sorted else 0,
        "p50": _percentile(cps_sorted, 50),
        "p95": _percentile(cps_sorted, 95),
        "max": cps_sorted[-1] if cps_sorted else 0,
    }

    elapsed_sec = max(0.0, ended_at - started_at)
    telem_summary = telem.summary()
    ratelimit_windows = int(telem_summary.get("ratelimit_windows", 0))
    metrics = {
        "run_id": run_id,
        "config": {
            "subreddit": cfg.probe.subreddit,
            "listing": cfg.probe.listing,
            "post_limit": cfg.probe.post_limit,
            "comment_sample": cfg.probe.comment_sample,
            "comment_replace_more_limit": cfg.probe.comment_replace_more_limit,
            "qpm_cap": cfg.probe.qpm_cap,
            "raw_json": cfg.probe.raw_json,
        },
        "timing": {
            "started_at": started_at,
            "ended_at": ended_at,
            "elapsed_sec": elapsed_sec,
        },
        "telemetry": telem_summary,
        "posts_count": len(posts),
        "comments_total": comments_total,
        "comments_per_expanded_post": per_post_stats,
    }

    # Local metrics/report writes disabled

    # Optional Supabase sink
    if cfg.supabase.enabled and cfg.supabase.url and cfg.supabase.key:
        sink = SupabaseSinkAdapter(cfg)
        run_row = {
            "run_id": run_id,
            "started_at": started_at,
            "ended_at": ended_at,
            "elapsed_sec": elapsed_sec,
            "subreddit": cfg.probe.subreddit,
            "listing": cfg.probe.listing,
            "post_limit": cfg.probe.post_limit,
            "comment_sample": cfg.probe.comment_sample,
            "replace_more_limit": cfg.probe.comment_replace_more_limit,
            "qpm_cap": cfg.probe.qpm_cap,
            "raw_json": cfg.probe.raw_json,
            "posts_count": len(posts),
            "comments_total": comments_total,
        }
        sink.upsert_run(run_row)
        logger.info("upserted run %s", run_id)
        # Upsert rows (idempotent)
        if posts_batch:
            sink.upsert_posts(posts_batch)
            logger.info("upserted %d posts", len(posts_batch))
        if comments_batch:
            sink.upsert_comments(comments_batch)
            logger.info("upserted %d comments", len(comments_batch))
        if post_ids_for_run:
            sink.link_run_posts(run_id, post_ids_for_run)
            logger.info("linked %d runs_posts", len(post_ids_for_run))
        if comment_ids_for_run:
            sink.link_run_comments(run_id, comment_ids_for_run)
            logger.info("linked %d runs_comments", len(comment_ids_for_run))

    logger.info("finished run %s elapsed=%.2fs", run_id, elapsed_sec)
    print(json.dumps({"run_id": run_id, "posts": len(posts), "comments": comments_total}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

def _configure_logging() -> None:
    level_name = os.getenv("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)
    log_format = "%(asctime)s %(levelname)s %(name)s: %(message)s"
    if os.getenv("LOG_JSON") == "1":
        # Minimal JSON formatter
        log_format = (
            '{"ts":"%(asctime)s","level":"%(levelname)s",'
            '"logger":"%(name)s","msg":"%(message)s"}'
        )
    # In AWS Lambda, logging may be pre-configured; force ensures our config applies
    try:
        logging.basicConfig(level=level, format=log_format, force=True)
    except TypeError:
        # Fallback for older environments without force param
        root = logging.getLogger()
        for h in list(root.handlers):
            root.removeHandler(h)
        logging.basicConfig(level=level, format=log_format)



