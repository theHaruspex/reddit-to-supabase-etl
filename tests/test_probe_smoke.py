from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from reddit_researcher.probe import main


@patch("reddit_researcher.probe.fetch_comments")
@patch("reddit_researcher.probe.iter_hot")
@patch("reddit_researcher.probe.load_config")
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
            out_dir=str(tmp_path / "data"),
            reports_dir=str(tmp_path / "reports"),
        ),
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

    # Verify outputs
    out_dir = Path(cfg.probe.out_dir)
    posts_files = list(out_dir.glob("posts_*.jsonl"))
    comments_files = list(out_dir.glob("comments_*.jsonl"))
    metrics_files = list(out_dir.glob("run_metrics_*.json"))
    assert posts_files and comments_files and metrics_files

    data = json.loads(metrics_files[0].read_text())
    assert data["posts_count"] == 2
    assert data["comments_total"] >= 1


