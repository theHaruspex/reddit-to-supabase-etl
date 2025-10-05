from __future__ import annotations

from collections.abc import Iterable, Iterator
from typing import Any, Protocol


class RedditSource(Protocol):
    def iter_posts(
        self, subreddit: str, listing: str, time_filter: str, limit: int
    ) -> Iterator[Any]:
        ...

    def fetch_comments(self, submission_id: str, replace_more_limit: int) -> list[Any]:
        ...


class MetricsSink(Protocol):
    def upsert_run(self, row: dict[str, Any]) -> None:
        ...

    def upsert_posts(self, rows: Iterable[dict[str, Any]]) -> None:
        ...

    def upsert_comments(self, rows: Iterable[dict[str, Any]]) -> None:
        ...

    def link_run_posts(self, run_id: str, post_ids: Iterable[str]) -> None:
        ...

    def link_run_comments(self, run_id: str, comment_ids: Iterable[str]) -> None:
        ...


