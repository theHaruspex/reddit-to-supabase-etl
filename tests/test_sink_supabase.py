from __future__ import annotations

from unittest.mock import MagicMock

from reddit_researcher.apis.supabase.client import SupabaseHandle
from reddit_researcher.apis.supabase.sink import upsert_comments, upsert_posts, upsert_run


def make_mock_handle() -> SupabaseHandle:
    client = MagicMock()
    client.table.return_value.upsert.return_value.execute.return_value = None
    return SupabaseHandle(client=client, schema="public")


def test_upsert_run_calls_supabase() -> None:
    sb = make_mock_handle()
    upsert_run(sb, {"run_id": "r1"})
    sb.client.table.assert_called_with("runs")


def test_upsert_posts_and_comments() -> None:
    sb = make_mock_handle()
    upsert_posts(sb, [{"id": "t3_a"}, {"id": "t3_b"}])
    upsert_comments(sb, [{"id": "t1_x"}])
    assert sb.client.table.call_count >= 2


