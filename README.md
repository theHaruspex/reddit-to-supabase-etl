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
- Probe (writes JSONL + metrics + report):
```bash
reddit-probe
```
- Hello CLI:
```bash
reddit-researcher
```

## Outputs
- `data/posts_YYYYMMDD_HHMM.jsonl` — normalized posts
- `data/comments_YYYYMMDD_HHMM.jsonl` — normalized comments for sampled posts
- `data/run_metrics_YYYYMMDD_HHMM.json` — metrics and telemetry
- `reports/run_YYYYMMDD_HHMM.md` — Markdown summary

## Development
- Lint, types, tests:
```bash
ruff check . && mypy src && pytest -q
```

## Notes
- Rate limiting enforced (token-bucket) with backoff helpers.
- Telemetry captures timings and parses X-Ratelimit-* headers when available.
