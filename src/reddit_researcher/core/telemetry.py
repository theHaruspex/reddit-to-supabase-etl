from __future__ import annotations

import time
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Stopwatch:
    started_at: float | None = None
    ended_at: float | None = None

    def start(self) -> None:
        if self.started_at is None:
            self.started_at = time.time()

    def stop(self) -> None:
        if self.ended_at is None:
            self.ended_at = time.time()

    @property
    def elapsed(self) -> float | None:
        if self.started_at is None:
            return None
        if self.ended_at is not None:
            return max(0.0, self.ended_at - self.started_at)
        return max(0.0, time.time() - self.started_at)

    def __enter__(self) -> Stopwatch:
        self.start()
        return self

    def __exit__(self, *_exc: Any) -> None:
        self.stop()


def parse_ratelimit_headers(headers: Mapping[str, str] | None) -> dict[str, float] | None:
    if not headers:
        return None
    # PRAW exposes lower-case header names when using requests; handle common cases
    used = headers.get("x-ratelimit-used") or headers.get("X-Ratelimit-Used")
    remaining = headers.get("x-ratelimit-remaining") or headers.get("X-Ratelimit-Remaining")
    reset = headers.get("x-ratelimit-reset") or headers.get("X-Ratelimit-Reset")
    if used is None and remaining is None and reset is None:
        return None
    result: dict[str, float] = {}
    if used is not None and _is_number(used):
        result["used"] = float(used)
    if remaining is not None and _is_number(remaining):
        result["remaining"] = float(remaining)
    if reset is not None and _is_number(reset):
        result["reset_sec"] = float(reset)
    return result or None


def _is_number(value: str) -> bool:
    try:
        float(value)
        return True
    except Exception:
        return False


@dataclass
class TelemetryRecorder:
    entries: list[dict[str, Any]] = field(default_factory=list)

    def record(
        self,
        endpoint: str,
        headers: Mapping[str, str] | None,
        elapsed_s: float | None,
    ) -> None:
        ratelimit = parse_ratelimit_headers(headers)
        self.entries.append(
            {
                "endpoint": endpoint,
                "elapsed_s": float(elapsed_s) if elapsed_s is not None else None,
                "ratelimit": ratelimit,
            }
        )

    def summary(self) -> dict[str, Any]:
        total = len(self.entries)
        rl_seen = [e.get("ratelimit") for e in self.entries if e.get("ratelimit")]
        return {
            "total": total,
            "ratelimit_windows": len(rl_seen),
        }


