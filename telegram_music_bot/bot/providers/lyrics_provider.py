from __future__ import annotations


class LyricsProvider:
    async def fetch_lyrics(self, query: str) -> str:
        return "Lyrics provider not configured. Set GENIUS_ACCESS_TOKEN to enable this feature."
