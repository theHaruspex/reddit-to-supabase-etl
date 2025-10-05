# Reddit APIs

This package encapsulates all communication with Reddit via PRAW.

## Responsibilities
- Build a read-only `praw.Reddit` client with a descriptive User-Agent.
- Fetch listing items (`hot`, `top`) with a configurable `limit`.
- Expand and collect comments with `replace_more(limit=…)` safeguards.
- Expose a small adapter (`RedditSourceAdapter`) that implements the core `RedditSource` port.

## How it fits in the flow
1) `core/probe.py` constructs `RedditSourceAdapter(cfg)`.
2) Probe asks the adapter for posts via `iter_posts(…)`.
3) Probe samples K posts and calls `fetch_comments(submission_id, replace_more_limit)`.
4) Probe normalizes the PRAW models (in `io/normalizers.py`) and persists/streams downstream.

## Key modules
- `reddit_client.py`:
  - `make_reddit(cfg) -> praw.Reddit`
  - Read-only mode; no write scopes required.
  - Ensure UA like: `theHaruspex:reddit-probe:v0.1 (by u/<reddit_username>)`.
- `listings.py`:
  - `iter_hot(reddit, subreddit, limit, raw_json=1)`
  - `iter_top(reddit, subreddit, time_filter, limit, raw_json=1)`
- `comments.py`:
  - `fetch_comments(reddit, submission_id, replace_more_limit, limiter=None)`
  - Uses PRAW’s `replace_more` to bound expansion.
- `adapter.py`:
  - `RedditSourceAdapter(cfg)` providing the `core/ports.py::RedditSource` interface.

## Rate limits and safety
- Probe enforces a client-side token-bucket QPM cap; PRAW also avoids abuse.
- Use conservative `replace_more_limit` (e.g., 5) for large threads.

## Data shapes
- PRAW models (`Submission`, `Comment`) are not persisted as-is.
- Probe converts them to dicts via `io/normalizers.py` for JSONL and DB upserts.

## Troubleshooting
- 401 Unauthorized: ensure `REDDIT_CLIENT_ID/SECRET` and correct User-Agent.
- Empty results: verify listing/time_filter and that your account/app has access.

See also: root README for overall flow, and `core/README.md` for orchestration.
