from __future__ import annotations

import random
import time
from collections.abc import Callable, Mapping
from dataclasses import dataclass


class RateLimiter:
    """Simple token-bucket rate limiter.

    Tokens refill continuously at qpm_cap/60 per second.
    Capacity is controlled by `burst_tokens`.
    `acquire()` will sleep as needed via the injected sleep function.
    """

    def __init__(
        self,
        qpm_cap: int,
        *,
        burst_tokens: float | int = 1.0,
        time_fn: Callable[[], float] | None = None,
        sleep_fn: Callable[[float], None] | None = None,
    ) -> None:
        if qpm_cap <= 0:
            raise ValueError("qpm_cap must be > 0")

        self._qpm_cap = float(qpm_cap)
        self._rate_per_sec = self._qpm_cap / 60.0
        self._capacity = max(1.0, float(burst_tokens))
        self._tokens = self._capacity
        self._time = time_fn or time.monotonic
        self._sleep = sleep_fn or time.sleep
        self._last_ts = self._time()

    def _refill(self) -> None:
        now = self._time()
        elapsed = max(0.0, now - self._last_ts)
        if elapsed > 0:
            self._tokens = min(self._capacity, self._tokens + elapsed * self._rate_per_sec)
            self._last_ts = now

    def acquire(self, cost: float = 1.0) -> None:
        if cost <= 0:
            return
        while True:
            self._refill()
            if self._tokens >= cost:
                self._tokens -= cost
                return
            deficit = cost - self._tokens
            wait_s = deficit / self._rate_per_sec
            self._sleep(wait_s)


def parse_retry_after(headers: Mapping[str, str] | None) -> float | None:
    if not headers:
        return None
    value = None
    for key in ("retry-after", "Retry-After", "RETRY-AFTER"):
        if key in headers:
            value = headers[key]
            break
    if value is None:
        return None
    value = value.strip()
    if value.isdigit():
        return float(int(value))
    # HTTP-date handling could be added; skipping for MVP
    return None


@dataclass(frozen=True)
class BackoffConfig:
    base: float = 0.5
    factor: float = 2.0
    jitter: float = 0.1  # proportion (e.g., 0.1 => ±10%)
    max_delay: float = 60.0


def compute_backoff_seconds(
    attempt: int,
    *,
    cfg: BackoffConfig | None = None,
    retry_after_s: float | None = None,
    rng: random.Random | None = None,
) -> float:
    """Return backoff seconds for a given attempt (0-based).

    If `retry_after_s` is provided, it is returned directly.
    """
    if retry_after_s is not None:
        return max(0.0, float(retry_after_s))

    if attempt < 0:
        attempt = 0
    cfg = cfg or BackoffConfig()
    delay = min(cfg.max_delay, cfg.base * (cfg.factor ** attempt))

    if cfg.jitter > 0:
        r = rng or random
        spread = cfg.jitter * delay
        jittered = delay + r.uniform(-spread, spread)
        return max(0.0, jittered)
    return max(0.0, delay)


