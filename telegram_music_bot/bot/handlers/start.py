from __future__ import annotations

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes


def require_services(context: ContextTypes.DEFAULT_TYPE):
    return context.application.bot_data["services"]


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = (
        "<b>Welcome to MusicBot Pro</b>
"
        "Queue tracks, manage playback, and run premium controls in private chats and groups.

"
        "Examples:
"
        "• <code>/play never gonna give you up</code>
"
        "• <code>/search daft punk</code>
"
        "• <code>/queue</code>"
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("▶️ Play", switch_inline_query_current_chat="/play ")],
        [InlineKeyboardButton("🔎 Search", switch_inline_query_current_chat="/search ")],
        [InlineKeyboardButton("⚙️ Settings", callback_data="settings:open")],
    ])
    await update.effective_message.reply_text(text, parse_mode="HTML", reply_markup=keyboard)
