from __future__ import annotations

from reddit_researcher.ratelimit import (
    BackoffConfig,
    RateLimiter,
    compute_backoff_seconds,
    parse_retry_after,
)


def test_rate_limiter_basic_spacing() -> None:
    # Simulate time: monotonic clock we control
    now = [0.0]

    def time_fn() -> float:
        return now[0]

    slept = []

    def sleep_fn(s: float) -> None:
        slept.append(round(s, 3))
        now[0] += s

    # 60 qpm => 1 per second
    rl = RateLimiter(60, burst_tokens=1, time_fn=time_fn, sleep_fn=sleep_fn)

    # First acquire consumes immediate token
    rl.acquire()
    # Second should sleep ~1s
    rl.acquire()

    assert slept and 0.9 <= slept[0] <= 1.1


def test_parse_retry_after_numeric() -> None:
    assert parse_retry_after({"Retry-After": "3"}) == 3.0
    assert parse_retry_after({"retry-after": "0"}) == 0.0
    assert parse_retry_after({}) is None
    assert parse_retry_after(None) is None


def test_compute_backoff_respects_retry_after() -> None:
    assert compute_backoff_seconds(0, retry_after_s=7.0) == 7.0


def test_compute_backoff_grows_and_jitters() -> None:
    cfg = BackoffConfig(base=0.5, factor=2.0, jitter=0.0, max_delay=10)
    assert compute_backoff_seconds(0, cfg=cfg) == 0.5
    assert compute_backoff_seconds(1, cfg=cfg) == 1.0
    assert compute_backoff_seconds(2, cfg=cfg) == 2.0
    assert compute_backoff_seconds(3, cfg=cfg) == 4.0
    assert compute_backoff_seconds(4, cfg=cfg) == 8.0


