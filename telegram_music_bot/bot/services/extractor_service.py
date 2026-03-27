from __future__ import annotations

from bot.models import Track
from bot.services.provider_router import ProviderRouter
from bot.utils.validators import ValidationError, is_url, validate_query, validate_url


class ExtractorService:
    def __init__(self, router: ProviderRouter) -> None:
        self.router = router

    async def search(self, query: str, user_id: int, user_name: str) -> list[Track]:
        return await self.router.search(validate_query(query), user_id, user_name)

    async def resolve(self, query_or_url: str, user_id: int, user_name: str, allow_urls: bool) -> Track:
        if is_url(query_or_url):
            if not allow_urls:
                raise ValidationError("URL mode is disabled in this chat")
            return await self.router.extract(validate_url(query_or_url), user_id, user_name)
        results = await self.search(query_or_url, user_id, user_name)
        if not results:
            raise ValidationError("No results found")
        return results[0]
