from __future__ import annotations

from bot.models import Track
from bot.providers.base import ProviderError, SearchProvider


class ProviderRouter:
    def __init__(self, providers: list[SearchProvider]) -> None:
        self.providers = providers

    async def search(self, query: str, user_id: int, user_name: str) -> list[Track]:
        for provider in self.providers:
            try:
                results = await provider.search(query, user_id, user_name)
                if results:
                    return results
            except Exception:
                continue
        raise ProviderError("No provider returned search results")

    async def extract(self, url: str, user_id: int, user_name: str) -> Track:
        for provider in self.providers:
            try:
                return await provider.extract(url, user_id, user_name)
            except Exception:
                continue
        raise ProviderError("Failed to extract track from URL")
