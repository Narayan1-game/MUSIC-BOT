from __future__ import annotations

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes


def require_services(context: ContextTypes.DEFAULT_TYPE):
    return context.application.bot_data["services"]


from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from bot.constants import COOLDOWN_SECONDS


async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    services = require_services(context)
    user = update.effective_user
    chat = update.effective_chat
    if not user or not chat:
        return
    limiter = services["rate_limiter"]
    allowed, wait = limiter.allow("search", chat.id, user.id, COOLDOWN_SECONDS["search"])
    if not allowed:
        await update.effective_message.reply_text(f"Please wait {wait}s before using /search again.")
        return
    query = " ".join(context.args).strip()
    if not query:
        await update.effective_message.reply_text("Usage: /search <query>")
        return
    await update.effective_message.reply_text("Searching…")
    tracks = await services["extractor"].search(query, user.id, user.full_name)
    codec = services["callback_codec"]
    kb = []
    for idx, track in enumerate(tracks, 1):
        payload = f"{idx}:{query[:20]}"
        cb = codec.encode("pick", chat.id, user.id, payload)
        kb.append([InlineKeyboardButton(f"{idx}. {track.title[:45]}", callback_data=cb)])
    await update.effective_message.reply_text("Select a result:", reply_markup=InlineKeyboardMarkup(kb))
