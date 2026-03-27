from __future__ import annotations

import logging
from telegram.error import TelegramError
from telegram import Update
from telegram.ext import ContextTypes


log = logging.getLogger(__name__)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    log.exception("Unhandled error", exc_info=context.error)
    if isinstance(update, Update) and update.effective_message:
        msg = "An unexpected error occurred. Please try again shortly."
        if isinstance(context.error, TelegramError):
            msg = "Telegram API error occurred. Please retry in a moment."
        try:
            await update.effective_message.reply_text(msg)
        except TelegramError:
            pass
