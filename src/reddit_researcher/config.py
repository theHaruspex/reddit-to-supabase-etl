from __future__ import annotations

import os
import time
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv


@dataclass(frozen=True)
class RedditConfig:
    client_id: str
    client_secret: str
    user_agent: str


@dataclass(frozen=True)
class ProbeConfig:
    subreddit: str = "all"
    listing: str = "hot"
    time_filter: str = "day"
    post_limit: int = 100
    comment_sample: int = 10
    comment_replace_more_limit: int = 5
    qpm_cap: int = 90
    max_runtime_sec: int = 600
    raw_json: int = 1
    out_dir: str = "./data"
    reports_dir: str = "./reports"


@dataclass(frozen=True)
class AppConfig:
    reddit: RedditConfig
    probe: ProbeConfig


def _expand_env(value: Any) -> Any:
    if isinstance(value, str):
        return os.path.expandvars(value)
    if isinstance(value, Mapping):
        return {k: _expand_env(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_expand_env(v) for v in value]
    return value


def load_config(config_path: str | Path = "config.yaml") -> AppConfig:
    # Load .env if present
    load_dotenv(override=False)

    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")

    with path.open("r", encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}

    raw = _expand_env(raw)

    reddit_raw = raw.get("reddit", {})
    probe_raw = raw.get("probe", {})

    reddit_cfg = RedditConfig(
        client_id=str(
            reddit_raw.get("client_id") or os.getenv("REDDIT_CLIENT_ID", "")
        ).strip(),
        client_secret=str(
            reddit_raw.get("client_secret") or os.getenv("REDDIT_CLIENT_SECRET", "")
        ).strip(),
        user_agent=str(
            reddit_raw.get(
                "user_agent",
                "theHaruspex:reddit-probe:v0.1 (by u/yourusername)",
            )
        ).strip(),
    )

    probe_cfg = ProbeConfig(
        subreddit=str(probe_raw.get("subreddit", ProbeConfig.subreddit)),
        listing=str(probe_raw.get("listing", ProbeConfig.listing)),
        time_filter=str(probe_raw.get("time_filter", ProbeConfig.time_filter)),
        post_limit=int(probe_raw.get("post_limit", ProbeConfig.post_limit)),
        comment_sample=int(
            probe_raw.get("comment_sample", ProbeConfig.comment_sample)
        ),
        comment_replace_more_limit=int(
            probe_raw.get(
                "comment_replace_more_limit",
                ProbeConfig.comment_replace_more_limit,
            )
        ),
        qpm_cap=int(probe_raw.get("qpm_cap", ProbeConfig.qpm_cap)),
        max_runtime_sec=int(
            probe_raw.get("max_runtime_sec", ProbeConfig.max_runtime_sec)
        ),
        raw_json=int(probe_raw.get("raw_json", ProbeConfig.raw_json)),
        out_dir=str(probe_raw.get("out_dir", ProbeConfig.out_dir)),
        reports_dir=str(probe_raw.get("reports_dir", ProbeConfig.reports_dir)),
    )

    # Ensure output dirs exist
    Path(probe_cfg.out_dir).mkdir(parents=True, exist_ok=True)
    Path(probe_cfg.reports_dir).mkdir(parents=True, exist_ok=True)

    return AppConfig(reddit=reddit_cfg, probe=probe_cfg)


def generate_run_id() -> str:
    return time.strftime("%Y%m%d_%H%M%S", time.gmtime())


