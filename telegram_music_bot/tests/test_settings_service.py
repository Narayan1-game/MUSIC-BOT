import asyncio

from bot.models import ChatSettings
from bot.services.settings_service import SettingsService


class DummyRepo:
    def __init__(self):
        self.settings = ChatSettings(chat_id=1)

    async def get_settings(self, chat_id, default_volume):
        return self.settings

    async def save_settings(self, settings):
        self.settings = settings


def test_toggle_bool_field():
    async def runner():
        svc = SettingsService(DummyRepo(), 100)
        updated = await svc.toggle(1, "admin_only_mode")
        assert updated.admin_only_mode is True

    asyncio.run(runner())
