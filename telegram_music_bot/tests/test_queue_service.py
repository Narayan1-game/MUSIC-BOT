import asyncio
from datetime import datetime, timezone

import pytest

from bot.models import Track
from bot.services.queue_service import QueueService


class DummyRepo:
    def __init__(self):
        self.items = []

    async def queue_items(self, chat_id):
        return self.items

    async def enqueue(self, chat_id, track):
        from bot.models import QueueItem

        item = QueueItem(id=len(self.items) + 1, chat_id=chat_id, position=len(self.items) + 1, track=track)
        self.items.append(item)
        return item


def test_queue_limit():
    async def runner():
        svc = QueueService(DummyRepo())
        track = Track(None, "x", None, "t", "u", None, 1, None, None, 1, "u", datetime.now(tz=timezone.utc), {})
        await svc.enqueue(1, track, 1)
        with pytest.raises(ValueError):
            await svc.enqueue(1, track, 1)

    asyncio.run(runner())
