from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes


HELP_TEXT = """<b>Help</b>\n\n<b>General</b>: /start /help /ping\n<b>Playback</b>: /play /search /nowplaying /pause /resume /skip /stop\n<b>Queue</b>: /queue /clear /remove /shuffle /repeat\n<b>Settings</b>: /settings /volume\n<b>Admin</b>: /stats /broadcast /maintenance /auditlog"""


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.effective_message.reply_text(HELP_TEXT, parse_mode="HTML")
