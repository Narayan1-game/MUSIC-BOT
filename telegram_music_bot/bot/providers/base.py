from __future__ import annotations

from typing import Protocol

from bot.models import Track


class ProviderError(Exception):
    pass


class SearchProvider(Protocol):
    name: str

    async def search(self, query: str, requested_by_user_id: int, requested_by_name: str) -> list[Track]: ...

    async def extract(self, url: str, requested_by_user_id: int, requested_by_name: str) -> Track: ...
