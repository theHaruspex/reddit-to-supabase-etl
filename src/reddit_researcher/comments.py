from __future__ import annotations

from typing import Any

import praw

from .ratelimit import RateLimiter


def fetch_comments(
    reddit: praw.Reddit,
    submission_id: str,
    *,
    replace_more_limit: int,
    limiter: RateLimiter | None = None,
) -> list[Any]:
    sub = reddit.submission(id=submission_id)
    if limiter:
        limiter.acquire()
    sub.comments.replace_more(limit=replace_more_limit)
    if limiter:
        limiter.acquire()
    return list(sub.comments.list())


