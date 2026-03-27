from __future__ import annotations

import time

from bot.models import BotHealthSnapshot
from bot.storage.repositories import Repository


class StatsService:
    def __init__(self, repo: Repository, capabilities: dict[str, bool], start_ts: float) -> None:
        self.repo = repo
        self.capabilities = capabilities
        self.start_ts = start_ts

    async def snapshot(self) -> BotHealthSnapshot:
        chats = await self.repo.conn.execute_fetchone("SELECT COUNT(*) c FROM chats")
        users = await self.repo.conn.execute_fetchone("SELECT COUNT(DISTINCT user_id) c FROM command_usage WHERE user_id IS NOT NULL")
        queued = await self.repo.conn.execute_fetchone("SELECT COUNT(*) c FROM queue_items")
        played = await self.repo.conn.execute_fetchone("SELECT COUNT(*) c FROM track_history")
        fail_e = await self.repo.conn.execute_fetchone("SELECT COUNT(*) c FROM bot_stats WHERE key='failed_extraction'")
        fail_p = await self.repo.conn.execute_fetchone("SELECT COUNT(*) c FROM bot_stats WHERE key='failed_playback'")
        return BotHealthSnapshot(
            uptime_seconds=int(time.time() - self.start_ts),
            total_chats=chats["c"],
            total_users=users["c"],
            total_tracks_queued=queued["c"],
            total_tracks_played=played["c"],
            failed_extractions=fail_e["c"],
            failed_playback=fail_p["c"],
            capabilities=self.capabilities,
        )
