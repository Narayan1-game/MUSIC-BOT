from __future__ import annotations

from bot.models import ChatSettings
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bot.storage.repositories import Repository


class SettingsService:
    def __init__(self, repo: Repository, default_volume: int) -> None:
        self.repo = repo
        self.default_volume = default_volume

    async def get(self, chat_id: int) -> ChatSettings:
        return await self.repo.get_settings(chat_id, self.default_volume)

    async def toggle(self, chat_id: int, field_name: str) -> ChatSettings:
        settings = await self.get(chat_id)
        if not hasattr(settings, field_name):
            raise ValueError("Unknown settings field")
        current = getattr(settings, field_name)
        if not isinstance(current, bool):
            raise ValueError("Only boolean fields can be toggled")
        setattr(settings, field_name, not current)
        await self.repo.save_settings(settings)
        return settings
