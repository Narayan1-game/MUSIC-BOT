from __future__ import annotations

import asyncio
import json
from pathlib import Path

from bot.models import Track
from bot.providers.base import ProviderError
from bot.utils.file_utils import unique_temp_path
from yt_dlp import YoutubeDL


class YtDlpProvider:
    name = "yt_dlp"

    def __init__(self, download_dir: Path, max_duration: int) -> None:
        self.download_dir = download_dir
        self.max_duration = max_duration

    async def search(self, query: str, requested_by_user_id: int, requested_by_name: str) -> list[Track]:
        loop = asyncio.get_running_loop()
        return await asyncio.wait_for(
            loop.run_in_executor(None, self._search_sync, query, requested_by_user_id, requested_by_name),
            timeout=20,
        )

    def _search_sync(self, query: str, user_id: int, user_name: str) -> list[Track]:
        opts = {"quiet": True, "skip_download": True, "extract_flat": "in_playlist"}
        with YoutubeDL(opts) as ydl:
            data = ydl.extract_info(f"ytsearch5:{query}", download=False)
        tracks: list[Track] = []
        for e in data.get("entries", [])[:5]:
            dur = e.get("duration")
            if dur and dur > self.max_duration:
                continue
            tracks.append(
                Track(
                    id=None,
                    source="youtube",
                    source_id=str(e.get("id", "")),
                    title=e.get("title", "Unknown"),
                    webpage_url=e.get("url") if str(e.get("url", "")).startswith("http") else f"https://www.youtube.com/watch?v={e.get('id')}",
                    stream_url=None,
                    duration_seconds=dur,
                    thumbnail_url=None,
                    uploader=e.get("uploader"),
                    requested_by_user_id=user_id,
                    requested_by_name=user_name,
                    extractor_metadata={"provider": self.name},
                )
            )
        return tracks

    async def extract(self, url: str, requested_by_user_id: int, requested_by_name: str) -> Track:
        loop = asyncio.get_running_loop()
        return await asyncio.wait_for(loop.run_in_executor(None, self._extract_sync, url, requested_by_user_id, requested_by_name), timeout=25)

    def _extract_sync(self, url: str, user_id: int, user_name: str) -> Track:
        out = unique_temp_path(self.download_dir, ".json")
        opts = {
            "quiet": True,
            "skip_download": True,
            "dump_single_json": True,
            "no_warnings": True,
            "noplaylist": True,
        }
        with YoutubeDL(opts) as ydl:
            data = ydl.extract_info(url, download=False)
        out.write_text(json.dumps(data), encoding="utf-8")
        dur = data.get("duration")
        if dur and dur > self.max_duration:
            raise ProviderError("Track duration exceeds policy limit")
        return Track(
            id=None,
            source=data.get("extractor_key", "yt_dlp"),
            source_id=str(data.get("id", "")),
            title=data.get("title", "Unknown"),
            webpage_url=data.get("webpage_url", url),
            stream_url=data.get("url"),
            duration_seconds=dur,
            thumbnail_url=data.get("thumbnail"),
            uploader=data.get("uploader"),
            requested_by_user_id=user_id,
            requested_by_name=user_name,
            extractor_metadata={"provider": self.name},
        )
