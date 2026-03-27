from __future__ import annotations

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes


def require_services(context: ContextTypes.DEFAULT_TYPE):
    return context.application.bot_data["services"]


from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from bot.utils.formatters import format_settings


async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    services = require_services(context)
    chat_id = update.effective_chat.id
    settings = await services["settings"].get(chat_id)
    codec = services["callback_codec"]
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("Toggle Admin-only", callback_data=codec.encode("stoggle", chat_id, 0, "admin_only_mode"))],
        [InlineKeyboardButton("Toggle URLs", callback_data=codec.encode("stoggle", chat_id, 0, "allow_url_mode"))],
        [InlineKeyboardButton("Toggle Thumbnails", callback_data=codec.encode("stoggle", chat_id, 0, "send_thumbnails"))],
    ])
    await update.effective_message.reply_text(format_settings(settings), parse_mode="HTML", reply_markup=kb)
