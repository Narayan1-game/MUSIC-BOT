from __future__ import annotations

from telegram import Message, Update
from telegram.ext import ContextTypes


class MessageService:
    async def send_or_edit(self, update: Update, context: ContextTypes.DEFAULT_TYPE, text: str, *, parse_mode: str = "HTML") -> Message:
        if update.callback_query and update.callback_query.message:
            await update.callback_query.message.edit_text(text, parse_mode=parse_mode, disable_web_page_preview=True)
            return update.callback_query.message
        return await update.effective_message.reply_text(text, parse_mode=parse_mode, disable_web_page_preview=True)
