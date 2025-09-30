from __future__ import annotations

from unittest.mock import patch

from reddit_researcher.api.reddit_client import make_reddit, make_user_agent
from reddit_researcher.config.config import AppConfig, ProbeConfig, RedditConfig


def test_make_user_agent_fallback() -> None:
    assert "unknown" not in make_user_agent("theHaruspex:reddit-probe:v0.1")
    assert "unknown" in make_user_agent("")


@patch("praw.Reddit")
def test_make_reddit_read_only(mock_reddit) -> None:
    cfg = AppConfig(
        reddit=RedditConfig(
            client_id="id",
            client_secret="secret",
            user_agent="theHaruspex:reddit-probe:v0.1 (by u/you)",
        ),
        probe=ProbeConfig(),
    )

    client = make_reddit(cfg)
    assert client == mock_reddit.return_value
    assert mock_reddit.return_value.read_only is True
    mock_reddit.assert_called_once()


