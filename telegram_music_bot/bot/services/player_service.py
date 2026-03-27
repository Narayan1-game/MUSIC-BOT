from __future__ import annotations

from bot.models import PlaybackState, QueueItem
from bot.storage.repositories import Repository
from bot.utils.time_utils import utcnow


class PlayerService:
    def __init__(self, repo: Repository, default_volume: int) -> None:
        self.repo = repo
        self.default_volume = default_volume

    async def get_state(self, chat_id: int) -> PlaybackState:
        state = await self.repo.get_playback_state(chat_id)
        if state:
            return state
        state = PlaybackState(
            chat_id=chat_id,
            current_queue_item_id=None,
            state="idle",
            repeat_mode="off",
            volume=self.default_volume,
            position_seconds=0,
            started_at=None,
            updated_at=utcnow(),
        )
        await self.repo.set_playback_state(state)
        return state

    async def start_item(self, chat_id: int, item: QueueItem) -> None:
        state = await self.get_state(chat_id)
        state.current_queue_item_id = item.id
        state.state = "playing"
        state.position_seconds = 0
        state.started_at = utcnow()
        state.updated_at = utcnow()
        await self.repo.set_playback_state(state)

    async def update_state(self, chat_id: int, new_state: str) -> PlaybackState:
        state = await self.get_state(chat_id)
        state.state = new_state
        state.updated_at = utcnow()
        await self.repo.set_playback_state(state)
        return state

    async def stop(self, chat_id: int) -> None:
        state = await self.get_state(chat_id)
        state.state = "idle"
        state.current_queue_item_id = None
        state.position_seconds = 0
        state.started_at = None
        state.updated_at = utcnow()
        await self.repo.set_playback_state(state)
