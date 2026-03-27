from __future__ import annotations

import asyncio
from collections import defaultdict

from bot.models import QueueItem, Track
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bot.storage.repositories import Repository


class QueueService:
    def __init__(self, repo: Repository) -> None:
        self.repo = repo
        self._locks: dict[int, asyncio.Lock] = defaultdict(asyncio.Lock)

    def lock(self, chat_id: int) -> asyncio.Lock:
        return self._locks[chat_id]

    async def enqueue(self, chat_id: int, track: Track, max_queue_length: int) -> QueueItem:
        async with self.lock(chat_id):
            items = await self.repo.queue_items(chat_id)
            if len(items) >= max_queue_length:
                raise ValueError("Queue limit reached")
            return await self.repo.enqueue(chat_id, track)

    async def get_queue(self, chat_id: int) -> list[QueueItem]:
        return await self.repo.queue_items(chat_id)

    async def pop_next(self, chat_id: int) -> QueueItem | None:
        async with self.lock(chat_id):
            return await self.repo.pop_next(chat_id)

    async def clear(self, chat_id: int) -> None:
        async with self.lock(chat_id):
            await self.repo.clear_queue(chat_id)

    async def remove(self, chat_id: int, index: int) -> bool:
        async with self.lock(chat_id):
            items = await self.repo.queue_items(chat_id)
            if index < 1 or index > len(items):
                return False
            target_id = items[index - 1].id
            await self.repo.conn.execute("DELETE FROM queue_items WHERE id=?", (target_id,))
            remaining = await (await self.repo.conn.execute("SELECT id FROM queue_items WHERE chat_id=? ORDER BY position", (chat_id,))).fetchall()
            for pos, row in enumerate(remaining, start=1):
                await self.repo.conn.execute("UPDATE queue_items SET position=? WHERE id=?", (pos, row[0]))
            await self.repo.conn.commit()
            return True
