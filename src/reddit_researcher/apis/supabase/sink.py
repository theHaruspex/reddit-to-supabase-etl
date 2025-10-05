from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from reddit_researcher.apis.supabase.client import SupabaseHandle


def upsert_rows(
    sb: SupabaseHandle, table: str, rows: Iterable[dict[str, Any]], *, conflict: str
) -> None:
    data = list(rows)
    if not data:
        return
    # supabase client: client.table(table).upsert(data, on_conflict=conflict)
    sb.client.table(table).upsert(data, on_conflict=conflict).execute()


def upsert_run(sb: SupabaseHandle, run_row: dict[str, Any]) -> None:
    upsert_rows(sb, "runs", [run_row], conflict="run_id")


def upsert_posts(sb: SupabaseHandle, posts: Iterable[dict[str, Any]]) -> None:
    upsert_rows(sb, "posts", posts, conflict="id")


def upsert_comments(sb: SupabaseHandle, comments: Iterable[dict[str, Any]]) -> None:
    upsert_rows(sb, "comments", comments, conflict="id")


