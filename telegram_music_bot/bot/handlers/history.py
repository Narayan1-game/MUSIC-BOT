from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes


async def history_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    s = context.bot_data["services"]
    lines = await s["history"].recent(update.effective_chat.id)
    await update.effective_message.reply_text("\n".join(lines) if lines else "No history yet.")
