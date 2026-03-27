from __future__ import annotations

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes


def require_services(context: ContextTypes.DEFAULT_TYPE):
    return context.application.bot_data["services"]


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = (
        "<b>Help</b>
"
        "<b>General</b>: /start /help /ping
"
        "<b>Playback</b>: /play /pause /resume /skip /stop /nowplaying
"
        "<b>Queue</b>: /queue /remove /clear /shuffle /repeat
"
        "<b>Settings</b>: /settings /volume
"
        "<b>Admin</b>: /stats /broadcast /maintenance /auditlog"
    )
    await update.effective_message.reply_text(text, parse_mode="HTML")
