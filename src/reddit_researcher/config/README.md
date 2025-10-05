# Config

Load and validate configuration from `.env` and `config.yaml`.

## How it works
- `config.py` loads `.env` (if present), then parses `config.yaml`.
- Expands `${ENV_VAR}` placeholders in YAML.
- Produces `AppConfig` with sections:
  - `reddit`: `client_id`, `client_secret`, `user_agent`
- `probe`: `subreddit`, `listing`, `post_limit`, `comment_sample`, `replace_more_limit`, `qpm_cap`, `raw_json`
  - `supabase`: `enabled`, `url`, `key`, `schema`

## Environment keys
- `REDDIT_CLIENT_ID`, `REDDIT_CLIENT_SECRET`
- `SUPABASE_URL`, `SUPABASE_KEY`

## Tips
- Keep secrets out of git; `.env` is ignored.
- Use a descriptive `user_agent` with your Reddit username.
