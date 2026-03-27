from __future__ import annotations

import time
from collections import defaultdict


class CooldownManager:
    def __init__(self) -> None:
        self._data: dict[tuple[int, int, str], float] = defaultdict(float)

    def allow(self, chat_id: int, user_id: int, key: str, cooldown_seconds: int) -> bool:
        now = time.monotonic()
        token = (chat_id, user_id, key)
        if now - self._data[token] < cooldown_seconds:
            return False
        self._data[token] = now
        return True
