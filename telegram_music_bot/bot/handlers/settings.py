from __future__ import annotations

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from bot.utils.formatters import format_settings


async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    s = context.bot_data["services"]
    chat_id = update.effective_chat.id
    settings = await s["settings"].get(chat_id)
    signer = s["signer"]
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("Toggle Admin-Only", callback_data=signer.sign(f"set:{chat_id}:admin_only_mode"))],
        [InlineKeyboardButton("Toggle URL Mode", callback_data=signer.sign(f"set:{chat_id}:allow_url_mode"))],
    ])
    await update.effective_message.reply_text(format_settings(settings), parse_mode="HTML", reply_markup=kb)
