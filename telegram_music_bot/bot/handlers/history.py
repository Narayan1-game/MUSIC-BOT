from __future__ import annotations

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes


def require_services(context: ContextTypes.DEFAULT_TYPE):
    return context.application.bot_data["services"]



async def history_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    services = require_services(context)
    chat_id = update.effective_chat.id
    items = await services["history"].list(chat_id, 10)
    if not items:
        await update.effective_message.reply_text("No history yet.")
        return
    lines = ["<b>Recent Tracks</b>"]
    for idx, i in enumerate(items, 1):
        lines.append(f"{idx}. {i['title']}")
    await update.effective_message.reply_text("
".join(lines), parse_mode="HTML")
