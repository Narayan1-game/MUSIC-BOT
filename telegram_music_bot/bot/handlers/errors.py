from __future__ import annotations

import logging

from telegram.error import TelegramError
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)


async def error_handler(update, context: ContextTypes.DEFAULT_TYPE) -> None:
    err = context.error
    if isinstance(err, TelegramError):
        logger.warning("Telegram API error: %s", err)
    else:
        logger.exception("Unhandled error", exc_info=err)
