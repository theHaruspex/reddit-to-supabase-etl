# Core

This package contains the orchestration runtime and cross-cutting utilities.

## Responsibilities
- Orchestrate the end-to-end probe run.
- Define ports (interfaces) to decouple core from API adapters.
- Provide rate limiting and telemetry helpers.

## Flow (probe)
1) Load config and configure logging.
2) Construct `RedditSourceAdapter` and (optionally) `SupabaseSinkAdapter`.
3) Fetch N posts from the listing; normalize and write to JSONL.
4) Sample K posts by `num_comments`; expand comments; normalize to JSONL.
5) Compute metrics (counts, per-post stats), write metrics JSON + Markdown report.
6) If Supabase enabled: upsert run, upsert posts/comments, link memberships.

## Ports
- `ports.py` defines:
  - `RedditSource`: `iter_posts(…)`, `fetch_comments(…)`
  - `MetricsSink`: `upsert_run`, `upsert_posts`, `upsert_comments`, `link_run_posts`, `link_run_comments`

## Logging
- `LOG_LEVEL=DEBUG|INFO|WARN|ERROR` (default INFO)
- `LOG_JSON=1` for JSON logs

## Utilities
- `ratelimit.py`: token-bucket limiter and backoff helpers
- `telemetry.py`: stopwatch and ratelimit header parsing
