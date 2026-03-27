from __future__ import annotations

from bot.models import Track
from bot.services.provider_router import ProviderRouter
from bot.utils.validators import is_valid_url


class ExtractorService:
    def __init__(self, router: ProviderRouter) -> None:
        self.router = router

    async def search(self, query: str, requester_id: int, requester_name: str) -> list[Track]:
        return await self.router.search(query, requester_id, requester_name)

    async def extract(self, query_or_url: str, requester_id: int, requester_name: str) -> Track:
        if query_or_url.startswith(("http://", "https://")) and not is_valid_url(query_or_url):
            raise ValueError("URL is not allowed")
        return await self.router.extract(query_or_url, requester_id, requester_name)
