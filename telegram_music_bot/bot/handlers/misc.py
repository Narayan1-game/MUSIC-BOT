from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes


async def import_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.effective_message.reply_text("Playlist/provider import architecture is ready. Full import adapters can be added safely.")


async def ping_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    pong = await context.bot_data["services"]["health"].ping()
    await update.effective_message.reply_text(f"🏓 {pong}")
