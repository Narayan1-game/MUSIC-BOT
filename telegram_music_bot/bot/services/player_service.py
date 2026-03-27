from __future__ import annotations

from datetime import datetime, timezone

from bot.models import PlaybackState, Track
from bot.storage.repositories import Repository


class PlayerService:
    """Playback-state service. Real streaming backend can be injected later."""

    def __init__(self, repo: Repository) -> None:
        self.repo = repo

    async def now(self, chat_id: int) -> tuple[Track | None, PlaybackState]:
        state = await self.repo.get_playback_state(chat_id)
        queue = await self.repo.get_queue(chat_id)
        return (queue[0].track if queue else None), state

    async def pause(self, chat_id: int) -> PlaybackState:
        state = await self.repo.get_playback_state(chat_id)
        if state.status != "playing":
            raise ValueError("Nothing is playing")
        state.status = "paused"
        await self.repo.save_playback_state(state)
        return state

    async def resume(self, chat_id: int) -> PlaybackState:
        state = await self.repo.get_playback_state(chat_id)
        if state.status != "paused":
            raise ValueError("Nothing is paused")
        state.status = "playing"
        await self.repo.save_playback_state(state)
        return state

    async def stop(self, chat_id: int) -> PlaybackState:
        state = await self.repo.get_playback_state(chat_id)
        state.status = "stopped"
        state.current_queue_item_id = None
        state.elapsed_seconds = 0
        await self.repo.save_playback_state(state)
        return state

    async def mark_playing(self, chat_id: int, queue_item_id: int | None) -> PlaybackState:
        state = await self.repo.get_playback_state(chat_id)
        state.status = "playing"
        state.current_queue_item_id = queue_item_id
        state.started_at = datetime.now(timezone.utc)
        await self.repo.save_playback_state(state)
        return state
