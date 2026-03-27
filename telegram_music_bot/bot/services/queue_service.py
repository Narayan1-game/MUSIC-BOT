from __future__ import annotations

import asyncio
from collections import defaultdict
import random

from bot.constants import RepeatMode
from bot.models import PlaybackState, QueueItem, Track
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bot.storage.repositories import Repository


class QueueService:
    def __init__(self, repo: "Repository") -> None:
        self.repo = repo
        self._locks: dict[int, asyncio.Lock] = defaultdict(asyncio.Lock)

    def lock_for(self, chat_id: int) -> asyncio.Lock:
        return self._locks[chat_id]

    async def enqueue(self, chat_id: int, track: Track, max_queue_length: int) -> QueueItem:
        async with self.lock_for(chat_id):
            queue = await self.repo.get_queue(chat_id)
            if len(queue) >= max_queue_length:
                raise ValueError("Queue is full for this chat")
            return await self.repo.enqueue_track(chat_id, track)

    async def queue(self, chat_id: int) -> list[QueueItem]:
        return await self.repo.get_queue(chat_id)

    async def remove(self, chat_id: int, index: int) -> bool:
        async with self.lock_for(chat_id):
            return await self.repo.remove_index(chat_id, index)

    async def clear(self, chat_id: int) -> int:
        async with self.lock_for(chat_id):
            return await self.repo.clear_queue(chat_id)

    async def shuffle(self, chat_id: int) -> None:
        async with self.lock_for(chat_id):
            items = await self.repo.get_queue(chat_id)
            if len(items) < 3:
                return
            first = items[0]
            rest = items[1:]
            random.shuffle(rest)
            await self.repo.clear_queue(chat_id)
            await self.repo.enqueue_track(chat_id, first.track)
            for item in rest:
                await self.repo.enqueue_track(chat_id, item.track)

    async def next_track(self, chat_id: int) -> QueueItem | None:
        async with self.lock_for(chat_id):
            state = await self.repo.get_playback_state(chat_id)
            if state.repeat_mode == RepeatMode.ONE and state.current_queue_item_id:
                queue = await self.repo.get_queue(chat_id)
                return queue[0] if queue else None
            item = await self.repo.pop_next(chat_id)
            return item

    async def set_repeat(self, chat_id: int, mode: str) -> PlaybackState:
        if mode not in {RepeatMode.OFF, RepeatMode.ONE, RepeatMode.ALL}:
            raise ValueError("Invalid repeat mode")
        state = await self.repo.get_playback_state(chat_id)
        state.repeat_mode = mode
        await self.repo.save_playback_state(state)
        return state
