from __future__ import annotations

from collections.abc import Iterator
from typing import Any

import praw


def iter_hot(
    reddit: praw.Reddit, subreddit: str, limit: int, *, raw_json: int = 1
) -> Iterator[Any]:
    sr = reddit.subreddit(subreddit)
    # Turn the PRAW ListingGenerator into a typed iterator
    yield from sr.hot(limit=limit)


def iter_top(
    reddit: praw.Reddit,
    subreddit: str,
    time_filter: str,
    limit: int,
    *,
    raw_json: int = 1,
) -> Iterator[Any]:
    sr = reddit.subreddit(subreddit)
    yield from sr.top(time_filter=time_filter, limit=limit)


