from __future__ import annotations

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from bot.constants import DEFAULT_PAGE_SIZE
from bot.utils.formatters import format_queue
from bot.utils.pagination import paginate


async def queue_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    s = context.bot_data["services"]
    chat = update.effective_chat
    if not chat:
        return
    items = await s["queue"].get_queue(chat.id)
    page = int(context.args[0]) if context.args and context.args[0].isdigit() else 1
    chunk, page, pages = paginate(items, page, DEFAULT_PAGE_SIZE)
    text = format_queue(None, chunk, page, pages, (await s["player"].get_state(chat.id)).repeat_mode)
    kb = []
    if pages > 1:
        kb.append([
            InlineKeyboardButton("◀️", callback_data=s["signer"].sign(f"q:{chat.id}:{page-1}")),
            InlineKeyboardButton("▶️", callback_data=s["signer"].sign(f"q:{chat.id}:{page+1}")),
        ])
    await update.effective_message.reply_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(kb) if kb else None)
