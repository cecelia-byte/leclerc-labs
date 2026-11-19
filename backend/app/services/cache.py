"""A tiny time-to-live cache.

OpenF1 allows only 30 requests per minute. Keeping recent answers in memory
means repeated page loads do not waste those requests.
"""

import time
from typing import Any


class TTLCache:
    def __init__(self) -> None:
        self._store: dict[str, tuple[float, Any]] = {}

    def get(self, key: str) -> Any | None:
        item = self._store.get(key)
        if item is None:
            return None

        expires_at, value = item
        if time.monotonic() >= expires_at:
            self._store.pop(key, None)
            return None

        return value

    def set(self, key: str, value: Any, ttl_seconds: int) -> None:
        self._store[key] = (time.monotonic() + ttl_seconds, value)

    def clear(self) -> None:
        self._store.clear()
