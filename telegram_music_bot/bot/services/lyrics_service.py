from __future__ import annotations

from bot.providers.lyrics_provider import LyricsProvider


class LyricsService:
    def __init__(self, provider: LyricsProvider) -> None:
        self.provider = provider

    async def get(self, query: str) -> str | None:
        return await self.provider.get_lyrics(query)
