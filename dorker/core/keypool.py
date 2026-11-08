from __future__ import annotations

import asyncio

from dorker.models import Key


class KeyPool:
    """Round-robin key pool that skips exhausted keys."""

    def __init__(self, keys: list[Key]):
        if not keys:
            raise ValueError("KeyPool requires at least one key")
        self._keys = list(keys)
        self._idx = -1
        self._exhausted: set[Key] = set()
        self._lock = asyncio.Lock()

    def __bool__(self) -> bool:
        return len(self._exhausted) < len(self._keys)

    @property
    def remaining(self) -> int:
        return len(self._keys) - len(self._exhausted)

    async def acquire(self) -> Key | None:
        async with self._lock:
            for _ in range(len(self._keys)):
                self._idx = (self._idx + 1) % len(self._keys)
                k = self._keys[self._idx]
                if k not in self._exhausted:
                    return k
            return None

    async def exhaust(self, key: Key) -> None:
        async with self._lock:
            self._exhausted.add(key)
