from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from reddit_researcher.core.probe import main


@patch("reddit_researcher.apis.reddit.adapter.RedditSourceAdapter.fetch_comments")
@patch("reddit_researcher.apis.reddit.adapter.RedditSourceAdapter.iter_posts")
@patch("reddit_researcher.core.probe.load_config")
def test_probe_smoke(mock_load_cfg, mock_iter_hot, mock_fetch_comments, tmp_path) -> None:
    cfg = SimpleNamespace(
        reddit=SimpleNamespace(client_id="id", client_secret="sec", user_agent="ua"),
        probe=SimpleNamespace(
            subreddit="all",
            listing="hot",
            time_filter="day",
            post_limit=2,
            comment_sample=1,
            comment_replace_more_limit=1,
            qpm_cap=100,
            max_runtime_sec=60,
            raw_json=1,
        ),
        supabase=SimpleNamespace(enabled=False, url="", key="", schema="public"),
    )
    mock_load_cfg.return_value = cfg

    posts = [
        SimpleNamespace(id="p1", num_comments=10, subreddit=SimpleNamespace(display_name="all")),
        SimpleNamespace(id="p2", num_comments=5, subreddit=SimpleNamespace(display_name="all")),
    ]
    mock_iter_hot.return_value = posts
    mock_fetch_comments.return_value = [
        SimpleNamespace(
            id="c1",
            link_id="t3_p1",
            parent_id="t3_p1",
            subreddit="all",
            author=SimpleNamespace(name="u"),
            body="b",
            created_utc=0,
            score=1,
            depth=0,
        )
    ]

    assert main([]) == 0

    # Verify core result printed JSON summary via return code; no local files expected


