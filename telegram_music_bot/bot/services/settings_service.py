from __future__ import annotations

from typing import Protocol

from bot.models import ChatSettings


class SettingsRepoProtocol(Protocol):
    async def get_settings(self, chat_id: int) -> ChatSettings: ...
    async def save_settings(self, settings: ChatSettings) -> None: ...


class SettingsService:
    def __init__(self, repo: SettingsRepoProtocol) -> None:
        self.repo = repo

    async def get(self, chat_id: int) -> ChatSettings:
        return await self.repo.get_settings(chat_id)

    async def toggle(self, chat_id: int, key: str) -> ChatSettings:
        settings = await self.repo.get_settings(chat_id)
        if not hasattr(settings, key):
            raise ValueError("Unknown settings key")
        value = getattr(settings, key)
        if not isinstance(value, bool):
            raise ValueError("Only bool toggles are supported")
        setattr(settings, key, not value)
        await self.repo.save_settings(settings)
        return settings
