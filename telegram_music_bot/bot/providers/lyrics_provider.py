from __future__ import annotations

import aiohttp


class LyricsProvider:
    def __init__(self, token: str | None) -> None:
        self.token = token

    async def get_lyrics(self, query: str) -> str | None:
        if not self.token:
            return None
        headers = {"Authorization": f"Bearer {self.token}"}
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
            async with session.get("https://api.genius.com/search", params={"q": query}, headers=headers) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()
                hits = data.get("response", {}).get("hits", [])
                if not hits:
                    return None
                return hits[0].get("result", {}).get("full_title")
