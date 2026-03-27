import asyncio
from bot.models import ChatSettings
from bot.services.settings_service import SettingsService


class Repo:
    def __init__(self):
        self.s = ChatSettings(chat_id=1)

    async def get_settings(self, chat_id):
        return self.s

    async def save_settings(self, settings):
        self.s = settings


def test_toggle_bool():
    async def run():
        svc = SettingsService(Repo())
        s = await svc.toggle(1, 'admin_only_mode')
        assert s.admin_only_mode is True
    asyncio.run(run())
