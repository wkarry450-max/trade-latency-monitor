from __future__ import annotations

import json
import os
import time
from typing import Any, Callable, Optional

try:
    import redis  # type: ignore
except Exception:  # pragma: no cover - import guard
    redis = None  # type: ignore


class Cache:
    """A tiny cache wrapper using Redis when available, otherwise in-memory.

    - Connects to Redis via REDIS_URL env or host/port.
    - Provides get/set_json helpers with TTL.
    - Fallback stores entries in a local dict with simple TTL handling.
    """

    def __init__(self) -> None:
        self._client = None
        self._memory_store: dict[str, tuple[float, str]] = {}

        url = os.getenv("REDIS_URL")
        host = os.getenv("REDIS_HOST", "127.0.0.1")
        port = int(os.getenv("REDIS_PORT", "6379"))

        if redis is not None:
            try:
                if url:
                    self._client = redis.Redis.from_url(url, decode_responses=True)
                else:
                    self._client = redis.Redis(host=host, port=port, decode_responses=True)
                # probe
                self._client.ping()
            except Exception:
                self._client = None

    @property
    def backend(self) -> str:
        return "redis" if self._client is not None else "memory"

    def get_json(self, key: str) -> Optional[Any]:
        if self._client is not None:
            value = self._client.get(key)
            return json.loads(value) if value is not None else None

        # memory fallback with TTL
        now = time.time()
        item = self._memory_store.get(key)
        if not item:
            return None
        expire_at, payload = item
        if now > expire_at:
            self._memory_store.pop(key, None)
            return None
        return json.loads(payload)

    def set_json(self, key: str, value: Any, ttl_seconds: int) -> None:
        payload = json.dumps(value, separators=(",", ":"))
        if self._client is not None:
            # PX requires milliseconds; use EX (seconds) for clarity
            self._client.set(key, payload, ex=ttl_seconds)
            return

        expire_at = time.time() + ttl_seconds
        self._memory_store[key] = (expire_at, payload)


