from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from bot.constants import RATE_LIMIT_LYRICS_SECONDS


async def lyrics_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    s = context.bot_data["services"]
    chat = update.effective_chat
    user = update.effective_user
    query = " ".join(context.args) or "current"
    if not s["cooldown"].allow(chat.id, user.id, "lyrics", RATE_LIMIT_LYRICS_SECONDS):
        await update.effective_message.reply_text("⏱ Try again shortly.")
        return
    lyrics = await s["lyrics"].get_lyrics(query)
    await update.effective_message.reply_text(lyrics[:3500])
