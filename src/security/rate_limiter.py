from __future__ import annotations

import time
from collections import defaultdict
from threading import Lock

_LOCK = Lock()
_REQUEST_TIMESTAMPS: dict[str, list[float]] = defaultdict(list)


def is_rate_limited(
    identifier: str,
    max_requests: int = 5,
    window_seconds: int = 600,  # 5 requests per 10 minutes default
) -> bool:
    """
    Thread-safe in-memory sliding-window rate limiter.
    Returns True if the identifier exceeds max_requests within window_seconds.
    """
    if not identifier:
        identifier = "anonymous"

    now = time.time()
    cutoff = now - window_seconds

    with _LOCK:
        timestamps = _REQUEST_TIMESTAMPS[identifier]
        # Keep only timestamps within window
        _REQUEST_TIMESTAMPS[identifier] = [ts for ts in timestamps if ts > cutoff]

        if len(_REQUEST_TIMESTAMPS[identifier]) >= max_requests:
            return True

        _REQUEST_TIMESTAMPS[identifier].append(now)
        return False


def reset_rate_limit(identifier: str | None = None) -> None:
    """Resets rate limit records (useful for testing or admin unblock)."""
    with _LOCK:
        if identifier:
            _REQUEST_TIMESTAMPS.pop(identifier, None)
        else:
            _REQUEST_TIMESTAMPS.clear()
