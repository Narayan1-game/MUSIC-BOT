from __future__ import annotations

from bot.services.stats_service import StatsService


class HealthService:
    def __init__(self, stats_service: StatsService) -> None:
        self.stats_service = stats_service

    async def ping(self) -> str:
        snapshot = await self.stats_service.snapshot()
        return f"PONG • uptime={snapshot.uptime_seconds}s • chats={snapshot.total_chats}"
