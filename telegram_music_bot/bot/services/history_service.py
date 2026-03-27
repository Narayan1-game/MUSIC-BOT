from __future__ import annotations

from bot.models import Track
from bot.storage.repositories import Repository


class HistoryService:
    def __init__(self, repo: Repository) -> None:
        self.repo = repo

    async def add(self, chat_id: int, track: Track) -> None:
        await self.repo.add_history(chat_id, track)

    async def list(self, chat_id: int, limit: int = 10) -> list[dict]:
        return await self.repo.get_history(chat_id, limit)
