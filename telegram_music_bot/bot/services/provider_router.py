from __future__ import annotations

from bot.models import Track
from bot.providers.base import BaseProvider, ProviderError


class ProviderRouter:
    def __init__(self, providers: list[BaseProvider]) -> None:
        self.providers = providers

    async def search(self, query: str, requester_id: int, requester_name: str) -> list[Track]:
        last_error: Exception | None = None
        for provider in self.providers:
            try:
                result = await provider.search(query, requester_id, requester_name)
                if result:
                    return result
            except ProviderError as exc:
                last_error = exc
        raise ProviderError(str(last_error or "No provider available"))

    async def extract(self, query_or_url: str, requester_id: int, requester_name: str) -> Track:
        last_error: Exception | None = None
        for provider in self.providers:
            try:
                return await provider.extract(query_or_url, requester_id, requester_name)
            except ProviderError as exc:
                last_error = exc
        raise ProviderError(str(last_error or "No provider available"))
