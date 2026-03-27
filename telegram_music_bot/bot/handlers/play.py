from __future__ import annotations

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes


def require_services(context: ContextTypes.DEFAULT_TYPE):
    return context.application.bot_data["services"]


from bot.constants import COOLDOWN_SECONDS
from bot.utils.formatters import format_track_line
from bot.utils.validators import ValidationError


async def play_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    services = require_services(context)
    user = update.effective_user
    chat = update.effective_chat
    if not user or not chat:
        return
    limiter = services["rate_limiter"]
    allowed, wait = limiter.allow("play", chat.id, user.id, COOLDOWN_SECONDS["play"])
    if not allowed:
        await update.effective_message.reply_text(f"Please wait {wait}s before using /play again.")
        return
    query = " ".join(context.args).strip()
    if not query:
        await update.effective_message.reply_text("Usage: /play <query or url>")
        return
    settings = await services["settings"].get(chat.id)
    try:
        track = await services["extractor"].resolve(query, user.id, user.full_name, settings.allow_url_mode)
        item = await services["queue"].enqueue(chat.id, track, settings.max_queue_length)
        await services["repo"].record_command("play", chat.id, user.id)
    except ValidationError as exc:
        await update.effective_message.reply_text(str(exc))
        return
    except Exception:
        await update.effective_message.reply_text("Could not queue this track. Please try another query.")
        return
    await update.effective_message.reply_text(f"Queued at position {item.position}:
{format_track_line(track)}", parse_mode="HTML")
