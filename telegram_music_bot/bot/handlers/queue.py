from __future__ import annotations

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes


def require_services(context: ContextTypes.DEFAULT_TYPE):
    return context.application.bot_data["services"]


from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from bot.constants import QUEUE_PAGE_SIZE
from bot.utils.formatters import format_queue_page
from bot.utils.pagination import paginate


async def queue_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    services = require_services(context)
    chat = update.effective_chat
    if not chat:
        return
    page = int(context.args[0]) if context.args and context.args[0].isdigit() else 1
    items = await services["queue"].queue(chat.id)
    state = await services["repo"].get_playback_state(chat.id)
    p, start, end = paginate(len(items), QUEUE_PAGE_SIZE, page)
    view = items[start:end]
    total_pages = max(1, (len(items) + QUEUE_PAGE_SIZE - 1) // QUEUE_PAGE_SIZE)
    text = format_queue_page(view, p, total_pages, state.repeat_mode)
    kb = []
    codec = services["callback_codec"]
    if total_pages > 1:
        row = []
        if p > 1:
            row.append(InlineKeyboardButton("⬅️", callback_data=codec.encode("qpage", chat.id, 0, str(p - 1))))
        if p < total_pages:
            row.append(InlineKeyboardButton("➡️", callback_data=codec.encode("qpage", chat.id, 0, str(p + 1))))
        kb.append(row)
    await update.effective_message.reply_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(kb) if kb else None)
