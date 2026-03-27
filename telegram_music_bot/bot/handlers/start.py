from __future__ import annotations

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    kb = InlineKeyboardMarkup(
        [[InlineKeyboardButton("▶️ Play", callback_data="nav:play"), InlineKeyboardButton("📚 Help", callback_data="nav:help")]]
    )
    text = (
        "🎼 <b>Welcome to Premium Music Bot</b>\n"
        "Fast queueing, clean controls, and chat-specific playback workflow.\n\n"
        "Examples:\n<code>/play daft punk harder better faster stronger</code>\n<code>/queue</code>"
    )
    await update.effective_message.reply_text(text, parse_mode="HTML", reply_markup=kb)
