from __future__ import annotations

import time

from reddit_researcher.core.telemetry import (
    Stopwatch,
    TelemetryRecorder,
    parse_ratelimit_headers,
)


def test_stopwatch_context_manager() -> None:
    sw = Stopwatch()
    with sw:
        time.sleep(0.01)
    assert sw.elapsed is not None and sw.elapsed >= 0.01


def test_parse_ratelimit_headers_variants() -> None:
    h1 = {"x-ratelimit-used": "10", "x-ratelimit-remaining": "20", "x-ratelimit-reset": "60"}
    h2 = {"X-Ratelimit-Used": "1", "X-Ratelimit-Remaining": "2", "X-Ratelimit-Reset": "3"}
    assert parse_ratelimit_headers(h1) == {"used": 10.0, "remaining": 20.0, "reset_sec": 60.0}
    assert parse_ratelimit_headers(h2) == {"used": 1.0, "remaining": 2.0, "reset_sec": 3.0}
    assert parse_ratelimit_headers({}) is None
    assert parse_ratelimit_headers(None) is None


def test_recorder_collects_entries_and_summary() -> None:
    rec = TelemetryRecorder()
    rec.record("/api/v1/test", {"x-ratelimit-used": "5", "x-ratelimit-reset": "30"}, 0.123)
    rec.record("/api/v1/test2", {}, 0.050)
    s = rec.summary()
    assert s["total"] == 2
    assert s["ratelimit_windows"] == 1


