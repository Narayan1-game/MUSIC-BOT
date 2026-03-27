from __future__ import annotations

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes


def require_services(context: ContextTypes.DEFAULT_TYPE):
    return context.application.bot_data["services"]


from bot.constants import COOLDOWN_SECONDS
from bot.utils.formatters import format_settings


async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query or not update.effective_chat or not update.effective_user:
        return
    services = require_services(context)
    allowed, wait = services["rate_limiter"].allow("callback", update.effective_chat.id, update.effective_user.id, COOLDOWN_SECONDS["callback"])
    if not allowed:
        await query.answer(f"Wait {wait}s", show_alert=True)
        return
    try:
        decoded = services["callback_codec"].decode(query.data)
    except Exception:
        await query.answer("Invalid callback", show_alert=True)
        return
    if int(decoded["chat_id"]) != update.effective_chat.id:
        await query.answer("Callback expired for this chat", show_alert=True)
        return
    action = decoded["action"]
    if action == "stoggle":
        settings = await services["settings"].toggle(update.effective_chat.id, decoded["payload"])
        await query.edit_message_text(format_settings(settings), parse_mode="HTML")
        await query.answer("Updated")
    elif action == "qpage":
        context.args = [decoded["payload"]]
        from bot.handlers.queue import queue_command
        await queue_command(update, context)
        await query.answer()
    else:
        await query.answer("Action registered")
