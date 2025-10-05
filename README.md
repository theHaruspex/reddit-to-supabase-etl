# Reddit Researcher

CLI tools to probe Reddit listings with PRAW, stream results to JSONL, and summarize request costs.

## Setup
1) Python 3.12 and a venv
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
```

2) Configure credentials and defaults
- Copy `.env.example` to `.env` and set:
  - `REDDIT_CLIENT_ID`, `REDDIT_CLIENT_SECRET`
- Edit `config.yaml` (user_agent should include your Reddit username)

## Run
```bash
reddit-probe
```
- Hello CLI:
```bash
reddit-researcher
```

## Outputs
This pipeline no longer writes local files; results are upserted idempotently to Supabase.

## Development
- Lint, types, tests:
```bash
ruff check . && mypy src && pytest -q
```

## Notes
- Rate limiting enforced (token-bucket) with backoff helpers.
- Telemetry captures timings and parses X-Ratelimit-* headers when available.

## Table of Contents
- Module docs
  - [apis/reddit](src/reddit_researcher/apis/reddit/README.md)
  - [apis/supabase](src/reddit_researcher/apis/supabase/README.md)
  - [core](src/reddit_researcher/core/README.md)
  - [config](src/reddit_researcher/config/README.md)
  - [cli](src/reddit_researcher/cli/README.md)
- Database schema
  - [schema/README.md](schema/README.md)
  - [schema/erd.mmd](schema/erd.mmd)
