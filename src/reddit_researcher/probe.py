from __future__ import annotations

import json
import random
import sys
import time
from pathlib import Path

from .comments import fetch_comments
from .config import AppConfig, generate_run_id, load_config
from .io_streams import append_jsonl, append_jsonl_many
from .listings import iter_hot, iter_top
from .normalizers import normalize_comment, normalize_post
from .ratelimit import RateLimiter, compute_backoff_seconds
from .telemetry import Stopwatch, TelemetryRecorder


def main(argv: list[str] | None = None) -> int:
    _ = argv or sys.argv[1:]

    try:
        cfg: AppConfig = load_config("config.yaml")
    except FileNotFoundError as exc:
        print(str(exc))
        return 2

    run_id = generate_run_id()
    out_posts = Path(cfg.probe.out_dir) / f"posts_{run_id}.jsonl"
    out_comments = Path(cfg.probe.out_dir) / f"comments_{run_id}.jsonl"
    out_metrics = Path(cfg.probe.out_dir) / f"run_metrics_{run_id}.json"
    report_dir = Path(cfg.probe.reports_dir)
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / f"run_{run_id}.md"

    limiter = RateLimiter(cfg.probe.qpm_cap, burst_tokens=1)
    telem = TelemetryRecorder()
    started_at = time.time()

    # Build client lazily inside helpers
    from .reddit_client import make_reddit
    reddit = make_reddit(cfg)

    # Fetch posts
    if cfg.probe.listing == "hot":
        posts_iter = iter_hot(
            reddit=reddit,
            subreddit=cfg.probe.subreddit,
            limit=cfg.probe.post_limit,
            raw_json=cfg.probe.raw_json,
        )
    else:
        posts_iter = iter_top(
            reddit=reddit,
            subreddit=cfg.probe.subreddit,
            time_filter=cfg.probe.time_filter,
            limit=cfg.probe.post_limit,
            raw_json=cfg.probe.raw_json,
        )

    posts = []
    for s in posts_iter:
        limiter.acquire()
        posts.append(s)
        append_jsonl(out_posts, normalize_post(s))

    # Choose K posts to expand comments (by num_comments desc)
    posts_sorted = sorted(posts, key=lambda x: getattr(x, "num_comments", 0), reverse=True)
    sample = posts_sorted[: cfg.probe.comment_sample]

    # Expand comments with basic retry/backoff
    rng = random.Random()
    for s in sample:
        attempts = 0
        while True:
            try:
                with Stopwatch() as sw:
                    comments = fetch_comments(
                        reddit=reddit,
                        submission_id=getattr(s, "id", ""),
                        replace_more_limit=cfg.probe.comment_replace_more_limit,
                        limiter=limiter,
                    )
                telem.record(
                    endpoint="comments.fetch",
                    headers={},
                    elapsed_s=sw.elapsed,
                )
                append_jsonl_many(
                    out_comments,
                    (normalize_comment(c, link_id=getattr(s, "id", None)) for c in comments),
                )
                break
            except Exception:
                attempts += 1
                delay = compute_backoff_seconds(attempts - 1, rng=rng)
                time.sleep(delay)
                if attempts >= 5:
                    break

    ended_at = time.time()

    comments_total = 0
    if Path(out_comments).exists():
        with Path(out_comments).open("r", encoding="utf-8") as f:
            for _ in f:
                comments_total += 1

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
            "elapsed_sec": max(0.0, ended_at - started_at),
        },
        "telemetry": telem.summary(),
        "posts_count": len(posts),
        "comments_total": comments_total,
    }

    Path(out_metrics).write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    report_lines = [
        f"# Reddit Probe — r/{cfg.probe.subreddit} ({cfg.probe.listing}) — {run_id}",
        "",
        f"posts fetched: {len(posts)}",
        f"comments written: {comments_total}",
    ]
    report_path.write_text("\n".join(report_lines), encoding="utf-8")

    print(json.dumps({"run_id": run_id, "posts": len(posts), "comments": comments_total}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


