from __future__ import annotations

import praw

from .config import AppConfig, RedditConfig


def make_user_agent(base_agent: str) -> str:
    # Ensure user agent is descriptive and non-empty
    ua = base_agent.strip() if base_agent else "reddit-probe/0.1 (by u/unknown)"
    return ua


def make_reddit(cfg: AppConfig | RedditConfig) -> praw.Reddit:
    if isinstance(cfg, AppConfig):
        rcfg = cfg.reddit
    else:
        rcfg = cfg

    reddit = praw.Reddit(
        client_id=rcfg.client_id,
        client_secret=rcfg.client_secret,
        user_agent=make_user_agent(rcfg.user_agent),
        check_for_updates=False,
        ratelimit_seconds=0,
    )

    # Read-only by default for this probe
    reddit.read_only = True
    return reddit


