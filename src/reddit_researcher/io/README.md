# IO

Local IO and format utilities.

## Responsibilities
- Normalize PRAW models to stable dicts that match DB columns.

## Modules
- `io_streams.py`:
  - `write_jsonl(path, records)`
  - `append_jsonl(path, record)` / `append_jsonl_many(path, records)`
- `normalizers.py`:
  - `normalize_post(submission)`
  - `normalize_comment(comment, link_id=None)`

This module no longer writes local files. Shapes align with Supabase tables described in `schema/README.md`.
