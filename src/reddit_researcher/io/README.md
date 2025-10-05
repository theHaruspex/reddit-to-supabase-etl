# IO

Local IO and format utilities.

## Responsibilities
- Write newline-delimited JSON (`*.jsonl`) for posts and comments.
- Normalize PRAW models to stable dicts that match DB columns.

## Modules
- `io_streams.py`:
  - `write_jsonl(path, records)`
  - `append_jsonl(path, record)` / `append_jsonl_many(path, records)`
- `normalizers.py`:
  - `normalize_post(submission)`
  - `normalize_comment(comment, link_id=None)`

## Data contracts
- `posts_YYYYMMDD_HHMM.jsonl`: one normalized post per line.
- `comments_YYYYMMDD_HHMM.jsonl`: one normalized comment per line.

These shapes align with the Supabase tables described in `schema/README.md`.
