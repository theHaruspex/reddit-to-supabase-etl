# Supabase APIs

This package encapsulates persistence to Supabase/Postgres via the Supabase Python client.

## Responsibilities
- Create a client from `SUPABASE_URL` and `SUPABASE_KEY`.
- Provide idempotent upserts for `runs`, `posts`, `comments` and membership link tables.
- Expose `SupabaseSinkAdapter` implementing the core `MetricsSink` port.

## How it fits in the flow
1) `core/probe.py` constructs `SupabaseSinkAdapter(cfg)` when `supabase.enabled=1`.
2) Probe upserts the `run` row (summary of config and counts).
3) Probe upserts normalized `posts` and `comments` batches.
4) Probe links `run_id` to `post_id` and `comment_id` in membership tables.

## Idempotency (ON CONFLICT)
- `runs(run_id)` upsert; updates elapsed/counts.
- `posts(id)` upsert; updates score, num_comments, retrieved_at.
- `comments(id)` upsert; updates score, retrieved_at.
- `runs_posts(run_id, post_id)` and `runs_comments(run_id, comment_id)` DO NOTHING to avoid duplicates.

## Migrations
- SQL files reside in `migrations/`; apply them via Supabase SQL editor or a Postgres connection.
- Minimal DDL: `runs`, `posts`, `comments`, `runs_posts`, `runs_comments`.

## Configuration
- `config.yaml` → `supabase.enabled`, `url`, `key`, `schema` (default `public`).
- Secrets via `.env`: `SUPABASE_URL`, `SUPABASE_KEY`.

## Troubleshooting
- PGRST205 “table not in schema cache”: run migrations in Supabase first.
- RLS: using service-role key bypasses RLS; for production, enable policies.

See also: `schema/README.md` for ERD and DDL; `core/README.md` for orchestration.
