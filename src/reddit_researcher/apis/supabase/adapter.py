from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from reddit_researcher.apis.supabase.client import make_supabase
from reddit_researcher.apis.supabase.sink import (
    upsert_comments,
    upsert_posts,
    upsert_run,
)
from reddit_researcher.config.config import AppConfig


class SupabaseSinkAdapter:
    def __init__(self, cfg: AppConfig) -> None:
        self._cfg = cfg
        self._sb = make_supabase(cfg.supabase.url, cfg.supabase.key, cfg.supabase.schema)

    def upsert_run(self, row: dict[str, Any]) -> None:
        upsert_run(self._sb, row)

    def upsert_posts(self, rows: Iterable[dict[str, Any]]) -> None:
        upsert_posts(self._sb, rows)

    def upsert_comments(self, rows: Iterable[dict[str, Any]]) -> None:
        upsert_comments(self._sb, rows)

    def link_run_posts(self, run_id: str, post_ids: Iterable[str]) -> None:
        # Optional future: implement runs_posts upsert
        pass

    def link_run_comments(self, run_id: str, comment_ids: Iterable[str]) -> None:
        # Optional future: implement runs_comments upsert
        pass


