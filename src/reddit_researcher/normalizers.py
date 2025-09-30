from __future__ import annotations

from datetime import UTC, datetime
from typing import Any


def _ts_to_iso(ts: Any) -> str | None:
    try:
        t = float(ts)
    except Exception:
        return None
    return datetime.fromtimestamp(t, tz=UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def normalize_post(submission: Any) -> dict[str, Any]:
    return {
        "id": getattr(submission, "id", None),
        "subreddit": (
            getattr(getattr(submission, "subreddit", None), "display_name", None)
            or getattr(submission, "subreddit", None)
        ),
        "title": getattr(submission, "title", None),
        "selftext": getattr(submission, "selftext", None),
        "url": getattr(submission, "url", None),
        "domain": getattr(submission, "domain", None),
        "author": getattr(getattr(submission, "author", None), "name", None),
        "created_utc": _ts_to_iso(getattr(submission, "created_utc", None)),
        "score": getattr(submission, "score", None),
        "num_comments": getattr(submission, "num_comments", None),
        "over_18": getattr(submission, "over_18", None),
        "upvote_ratio": getattr(submission, "upvote_ratio", None),
        "permalink": getattr(submission, "permalink", None),
        "retrieved_at": _ts_to_iso(datetime.now(tz=UTC).timestamp()),
    }


def normalize_comment(comment: Any, link_id: str | None = None) -> dict[str, Any]:
    cid = getattr(comment, "id", None)
    link = link_id or getattr(comment, "link_id", None)
    parent_id = getattr(comment, "parent_id", None)
    return {
        "id": cid,
        "link_id": link,
        "parent_id": parent_id,
        "subreddit": (
            getattr(getattr(comment, "subreddit", None), "display_name", None)
            or getattr(comment, "subreddit", None)
        ),
        "author": getattr(getattr(comment, "author", None), "name", None),
        "body": getattr(comment, "body", None),
        "created_utc": _ts_to_iso(getattr(comment, "created_utc", None)),
        "score": getattr(comment, "score", None),
        "depth": getattr(comment, "depth", None),
        "retrieved_at": _ts_to_iso(datetime.now(tz=UTC).timestamp()),
    }


