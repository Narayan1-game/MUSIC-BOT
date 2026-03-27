from __future__ import annotations

import asyncio
from datetime import UTC, datetime

from yt_dlp import YoutubeDL

from bot.constants import YT_DLP_TIMEOUT_SECONDS
from bot.models import Track
from bot.providers.base import BaseProvider, ProviderError


class YtDlpProvider(BaseProvider):
    name = "yt-dlp"

    def _extract_sync(self, query: str, search: bool) -> dict:
        opts = {"quiet": True, "noplaylist": True}
        with YoutubeDL(opts) as ydl:
            if search:
                return ydl.extract_info(f"ytsearch5:{query}", download=False)
            return ydl.extract_info(query, download=False)

    def _to_track(self, item: dict, requester_id: int, requester_name: str) -> Track:
        return Track(
            id=None,
            source=self.name,
            source_id=str(item.get("id") or ""),
            title=item.get("title") or "Unknown",
            webpage_url=item.get("webpage_url") or item.get("original_url") or "",
            stream_url=item.get("url"),
            duration_seconds=item.get("duration"),
            thumbnail_url=item.get("thumbnail"),
            uploader=item.get("uploader"),
            requested_by_user_id=requester_id,
            requested_by_name=requester_name,
            added_at=datetime.now(tz=UTC),
            extractor_metadata={"extractor": item.get("extractor")},
        )

    async def search(self, query: str, requester_id: int, requester_name: str) -> list[Track]:
        try:
            data = await asyncio.wait_for(asyncio.to_thread(self._extract_sync, query, True), timeout=YT_DLP_TIMEOUT_SECONDS)
            entries = data.get("entries") or []
            return [self._to_track(e, requester_id, requester_name) for e in entries[:5] if e]
        except Exception as exc:  # noqa: BLE001
            raise ProviderError(f"Search failed: {exc}") from exc

    async def extract(self, url_or_query: str, requester_id: int, requester_name: str) -> Track:
        try:
            data = await asyncio.wait_for(asyncio.to_thread(self._extract_sync, url_or_query, False), timeout=YT_DLP_TIMEOUT_SECONDS)
            return self._to_track(data, requester_id, requester_name)
        except Exception as exc:  # noqa: BLE001
            raise ProviderError(f"Extract failed: {exc}") from exc
