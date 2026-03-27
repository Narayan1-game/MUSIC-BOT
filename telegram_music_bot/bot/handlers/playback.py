from __future__ import annotations

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes


def require_services(context: ContextTypes.DEFAULT_TYPE):
    return context.application.bot_data["services"]


from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from bot.utils.formatters import format_now_playing


async def nowplaying_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    services = require_services(context)
    chat = update.effective_chat
    if not chat:
        return
    track, state = await services["player"].now(chat.id)
    codec = services["callback_codec"]
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("⏯", callback_data=codec.encode("toggle", chat.id, 0, "")),
            InlineKeyboardButton("⏭", callback_data=codec.encode("skip", chat.id, 0, "")),
            InlineKeyboardButton("⏹", callback_data=codec.encode("stop", chat.id, 0, "")),
        ]
    ])
    await update.effective_message.reply_text(format_now_playing(track, state), parse_mode="HTML", reply_markup=keyboard)


async def pause_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    services = require_services(context)
    try:
        await services["player"].pause(update.effective_chat.id)
        await update.effective_message.reply_text("Paused.")
    except ValueError as exc:
        await update.effective_message.reply_text(str(exc))


async def resume_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    services = require_services(context)
    try:
        await services["player"].resume(update.effective_chat.id)
        await update.effective_message.reply_text("Resumed.")
    except ValueError as exc:
        await update.effective_message.reply_text(str(exc))


async def skip_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    services = require_services(context)
    chat_id = update.effective_chat.id
    item = await services["queue"].next_track(chat_id)
    if item is None:
        await services["player"].stop(chat_id)
        await update.effective_message.reply_text("Queue ended.")
        return
    await services["player"].mark_playing(chat_id, item.id)
    await services["history"].add(chat_id, item.track)
    await update.effective_message.reply_text(f"Skipped. Now playing: {item.track.title}")


async def stop_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    services = require_services(context)
    chat_id = update.effective_chat.id
    await services["player"].stop(chat_id)
    await services["queue"].clear(chat_id)
    await update.effective_message.reply_text("Playback stopped and queue cleared.")


async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    services = require_services(context)
    removed = await services["queue"].clear(update.effective_chat.id)
    await update.effective_message.reply_text(f"Cleared {removed} queued tracks.")


async def remove_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    services = require_services(context)
    if not context.args or not context.args[0].isdigit():
        await update.effective_message.reply_text("Usage: /remove <index>")
        return
    ok = await services["queue"].remove(update.effective_chat.id, int(context.args[0]))
    await update.effective_message.reply_text("Removed." if ok else "Index not found.")


async def shuffle_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    services = require_services(context)
    await services["queue"].shuffle(update.effective_chat.id)
    await update.effective_message.reply_text("Queue shuffled.")


async def repeat_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    services = require_services(context)
    mode = (context.args[0].lower() if context.args else "off")
    try:
        state = await services["queue"].set_repeat(update.effective_chat.id, mode)
        await update.effective_message.reply_text(f"Repeat mode set to {state.repeat_mode}.")
    except ValueError:
        await update.effective_message.reply_text("Usage: /repeat off|one|all")


async def volume_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    services = require_services(context)
    if not context.args or not context.args[0].isdigit():
        await update.effective_message.reply_text("Usage: /volume <1-100>")
        return
    volume = int(context.args[0])
    if volume < 1 or volume > 100:
        await update.effective_message.reply_text("Volume must be 1..100")
        return
    state = await services["repo"].get_playback_state(update.effective_chat.id)
    state.volume = volume
    await services["repo"].save_playback_state(state)
    await update.effective_message.reply_text(f"Volume set to {volume}%.")
