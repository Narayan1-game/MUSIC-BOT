from __future__ import annotations

import time
from collections import defaultdict


class RateLimiter:
    def __init__(self) -> None:
        self._last: dict[tuple[str, int, int], float] = defaultdict(float)

    def allow(self, action: str, chat_id: int, user_id: int, cooldown: int) -> tuple[bool, int]:
        now = time.monotonic()
        key = (action, chat_id, user_id)
        elapsed = now - self._last[key]
        if elapsed < cooldown:
            return False, max(1, int(cooldown - elapsed))
        self._last[key] = now
        return True, 0
