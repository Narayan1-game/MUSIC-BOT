from __future__ import annotations

from bot.storage.repositories import Repository


class HistoryService:
    def __init__(self, repo: Repository) -> None:
        self.repo = repo

    async def recent(self, chat_id: int, limit: int = 10) -> list[str]:
        rows = await self.repo.history(chat_id, limit)
        return [f"{r['title']} ({r['played_at']})" for r in rows]
