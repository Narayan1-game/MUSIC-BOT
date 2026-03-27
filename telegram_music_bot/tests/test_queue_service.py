import asyncio
from types import SimpleNamespace

from bot.models import Track
from bot.services.queue_service import QueueService


class DummyRepo:
    def __init__(self):
        self.items = []
        self.state = SimpleNamespace(repeat_mode='off', current_queue_item_id=None)

    async def get_queue(self, chat_id):
        return self.items

    async def enqueue_track(self, chat_id, track):
        item = SimpleNamespace(id=len(self.items)+1, chat_id=chat_id, position=len(self.items)+1, track=track)
        self.items.append(item)
        return item

    async def remove_index(self, chat_id, index):
        if index < 1 or index > len(self.items):
            return False
        self.items.pop(index-1)
        return True

    async def clear_queue(self, chat_id):
        n = len(self.items)
        self.items = []
        return n

    async def get_playback_state(self, chat_id):
        return self.state

    async def pop_next(self, chat_id):
        return self.items.pop(0) if self.items else None

    async def save_playback_state(self, state):
        self.state = state


def test_enqueue_and_clear():
    async def run():
        repo = DummyRepo()
        svc = QueueService(repo)
        t = Track(None, 'yt', '1', 'Song', None, None, 10, None, None, 1, 'u')
        await svc.enqueue(1, t, 5)
        assert len(await svc.queue(1)) == 1
        assert await svc.clear(1) == 1
    asyncio.run(run())
