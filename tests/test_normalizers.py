from __future__ import annotations

from types import SimpleNamespace

from reddit_researcher.normalizers import normalize_comment, normalize_post


def test_normalize_post_basic() -> None:
    sub = SimpleNamespace(display_name="all")
    author = SimpleNamespace(name="alice")
    s = SimpleNamespace(
        id="t3_abc",
        subreddit=sub,
        title="hello",
        selftext="body",
        url="https://example.com",
        domain="example.com",
        author=author,
        created_utc=1_700_000_000,
        score=10,
        num_comments=5,
        over_18=False,
        upvote_ratio=0.9,
        permalink="/r/all/comments/abc/hello/",
    )
    rec = normalize_post(s)
    assert rec["id"] == "t3_abc"
    assert rec["subreddit"] == "all"
    assert rec["author"] == "alice"
    assert rec["title"] == "hello"
    assert rec["created_utc"].endswith("Z")


def test_normalize_comment_basic() -> None:
    sub = SimpleNamespace(display_name="all")
    author = SimpleNamespace(name="bob")
    c = SimpleNamespace(
        id="t1_xyz",
        link_id="t3_abc",
        parent_id="t3_abc",
        subreddit=sub,
        author=author,
        body="hi",
        created_utc=1_700_000_100,
        score=3,
        depth=1,
    )
    rec = normalize_comment(c)
    assert rec["id"] == "t1_xyz"
    assert rec["link_id"] == "t3_abc"
    assert rec["author"] == "bob"
    assert rec["created_utc"].endswith("Z")


