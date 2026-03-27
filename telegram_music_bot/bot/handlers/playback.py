from __future__ import annotations

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from bot.utils.formatters import format_now_playing


async def nowplaying_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    s = context.bot_data["services"]
    chat = update.effective_chat
    if not chat:
        return
    state = await s["player"].get_state(chat.id)
    items = await s["queue"].get_queue(chat.id)
    current = items[0] if items else None
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("⏯", callback_data=s["signer"].sign(f"ctl:{chat.id}:toggle")), InlineKeyboardButton("⏭", callback_data=s["signer"].sign(f"ctl:{chat.id}:skip"))]])
    await update.effective_message.reply_text(format_now_playing(current, state), parse_mode="HTML", reply_markup=kb)


async def pause_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    s = context.bot_data["services"]
    await s["player"].update_state(update.effective_chat.id, "paused")
    await update.effective_message.reply_text("⏸ Paused.")


async def resume_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    s = context.bot_data["services"]
    await s["player"].update_state(update.effective_chat.id, "playing")
    await update.effective_message.reply_text("▶️ Resumed.")


async def skip_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    s = context.bot_data["services"]
    chat_id = update.effective_chat.id
    item = await s["queue"].pop_next(chat_id)
    if item:
        await s["repo"].add_history(chat_id, item)
        await s["repo"].increment_stat("tracks_played")
    nxt = await s["queue"].get_queue(chat_id)
    if nxt:
        await s["player"].start_item(chat_id, nxt[0])
        await update.effective_message.reply_text(f"⏭ Skipped. Now: {nxt[0].track.title}")
    else:
        await s["player"].stop(chat_id)
        await update.effective_message.reply_text("⏹ Queue ended.")


async def stop_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    s = context.bot_data["services"]
    chat_id = update.effective_chat.id
    await s["player"].stop(chat_id)
    await s["queue"].clear(chat_id)
    await update.effective_message.reply_text("⏹ Stopped and queue cleared.")


async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    s = context.bot_data["services"]
    await s["queue"].clear(update.effective_chat.id)
    await update.effective_message.reply_text("🧹 Queue cleared.")


async def remove_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    s = context.bot_data["services"]
    if not context.args or not context.args[0].isdigit():
        await update.effective_message.reply_text("Usage: /remove <index>")
        return
    ok = await s["queue"].remove(update.effective_chat.id, int(context.args[0]))
    await update.effective_message.reply_text("✅ Removed." if ok else "Invalid index.")


async def repeat_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    s = context.bot_data["services"]
    state = await s["player"].get_state(update.effective_chat.id)
    modes = ["off", "one", "all"]
    next_mode = modes[(modes.index(state.repeat_mode) + 1) % len(modes)]
    state.repeat_mode = next_mode
    await s["repo"].set_playback_state(state)
    await update.effective_message.reply_text(f"🔁 Repeat mode: {next_mode}")


async def shuffle_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.effective_message.reply_text("🔀 Shuffle queued (placeholder for deterministic reorder).")


async def volume_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    s = context.bot_data["services"]
    if not context.args or not context.args[0].isdigit():
        await update.effective_message.reply_text("Usage: /volume <1-100>")
        return
    value = max(1, min(100, int(context.args[0])))
    state = await s["player"].get_state(update.effective_chat.id)
    state.volume = value
    await s["repo"].set_playback_state(state)
    await update.effective_message.reply_text(f"🔊 Volume set to {value}%")
