from __future__ import annotations

from unittest.mock import MagicMock

from reddit_researcher.listings import iter_hot, iter_top


def test_iter_hot_calls_praw() -> None:
    reddit = MagicMock()
    reddit.subreddit.return_value.hot.return_value = [1, 2, 3]
    items = list(iter_hot(reddit, "all", limit=3))
    assert items == [1, 2, 3]
    reddit.subreddit.assert_called_once_with("all")


def test_iter_top_calls_praw() -> None:
    reddit = MagicMock()
    reddit.subreddit.return_value.top.return_value = ["a"]
    items = list(iter_top(reddit, "all", time_filter="day", limit=1))
    assert items == ["a"]
    reddit.subreddit.assert_called_once_with("all")


