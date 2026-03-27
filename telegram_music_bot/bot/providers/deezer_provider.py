from __future__ import annotations

from bot.models import Track
from bot.providers.base import BaseProvider, ProviderError


class DeezerProvider(BaseProvider):
    name = "deezer"

    async def search(self, query: str, requester_id: int, requester_name: str) -> list[Track]:
        raise ProviderError("Deezer provider not configured")

    async def extract(self, url_or_query: str, requester_id: int, requester_name: str) -> Track:
        raise ProviderError("Deezer provider not configured")
