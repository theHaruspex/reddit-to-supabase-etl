from __future__ import annotations

from collections.abc import Iterator
from typing import Any

from reddit_researcher.apis.reddit.comments import fetch_comments as _fetch_comments
from reddit_researcher.apis.reddit.listings import iter_hot, iter_top
from reddit_researcher.apis.reddit.reddit_client import make_reddit
from reddit_researcher.config.config import AppConfig


class RedditSourceAdapter:
    def __init__(self, cfg: AppConfig) -> None:
        self._cfg = cfg
        self._client = make_reddit(cfg)

    def iter_posts(
        self, subreddit: str, listing: str, time_filter: str, limit: int
    ) -> Iterator[Any]:
        if listing == "hot":
            return iter_hot(
                self._client,
                subreddit=subreddit,
                limit=limit,
                raw_json=self._cfg.probe.raw_json,
            )
        return iter_top(
            self._client,
            subreddit=subreddit,
            time_filter=time_filter,
            limit=limit,
            raw_json=self._cfg.probe.raw_json,
        )

    def fetch_comments(self, submission_id: str, replace_more_limit: int) -> list[Any]:
        return _fetch_comments(
            self._client,
            submission_id=submission_id,
            replace_more_limit=replace_more_limit,
            limiter=None,
        )


