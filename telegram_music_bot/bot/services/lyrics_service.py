from __future__ import annotations

from bot.providers.lyrics_provider import LyricsProvider


class LyricsService:
    def __init__(self, provider: LyricsProvider) -> None:
        self.provider = provider

    async def get_lyrics(self, query: str) -> str:
        return await self.provider.fetch_lyrics(query)
