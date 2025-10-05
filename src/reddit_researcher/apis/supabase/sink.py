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


def link_run_posts(sb: SupabaseHandle, run_id: str, post_ids: Iterable[str]) -> None:
    rows = [{"run_id": run_id, "post_id": pid} for pid in set(post_ids)]
    if not rows:
        return
    sb.client.table("runs_posts").upsert(rows, on_conflict="run_id,post_id").execute()


def link_run_comments(sb: SupabaseHandle, run_id: str, comment_ids: Iterable[str]) -> None:
    rows = [{"run_id": run_id, "comment_id": cid} for cid in set(comment_ids)]
    if not rows:
        return
    sb.client.table("runs_comments").upsert(rows, on_conflict="run_id,comment_id").execute()


