from __future__ import annotations

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes


def require_services(context: ContextTypes.DEFAULT_TYPE):
    return context.application.bot_data["services"]


from bot.constants import COOLDOWN_SECONDS


async def lyrics_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    services = require_services(context)
    user = update.effective_user
    chat = update.effective_chat
    if not user or not chat:
        return
    allowed, wait = services["rate_limiter"].allow("lyrics", chat.id, user.id, COOLDOWN_SECONDS["lyrics"])
    if not allowed:
        await update.effective_message.reply_text(f"Please wait {wait}s before using /lyrics again.")
        return
    query = " ".join(context.args).strip()
    if not query:
        await update.effective_message.reply_text("Usage: /lyrics <query>")
        return
    lyrics = await services["lyrics"].get(query)
    await update.effective_message.reply_text(lyrics or "No lyrics found.")
