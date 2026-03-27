from __future__ import annotations

from datetime import datetime

from bot.models import BotHealthSnapshot
from bot.storage.repositories import Repository


class StatsService:
    def __init__(self, repo: Repository, started_at: datetime, capabilities: dict[str, bool]) -> None:
        self.repo = repo
        self.started_at = started_at
        self.capabilities = capabilities

    async def snapshot(self) -> BotHealthSnapshot:
        return BotHealthSnapshot(
            uptime_seconds=int((datetime.utcnow() - self.started_at).total_seconds()),
            total_chats=await self.repo.count_chats(),
            total_users_seen=await self.repo.count_users(),
            total_tracks_queued=await self.repo.get_stat("tracks_queued"),
            total_tracks_played=await self.repo.get_stat("tracks_played"),
            failed_extraction_count=await self.repo.get_stat("failed_extraction"),
            failed_playback_count=await self.repo.get_stat("failed_playback"),
            capabilities=self.capabilities,
        )
