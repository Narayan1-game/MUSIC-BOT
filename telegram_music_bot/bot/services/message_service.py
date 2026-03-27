from __future__ import annotations

from telegram import Message


class MessageService:
    async def smart_reply(self, source: Message, text: str) -> Message:
        return await source.reply_text(text, parse_mode="HTML", disable_web_page_preview=True)
