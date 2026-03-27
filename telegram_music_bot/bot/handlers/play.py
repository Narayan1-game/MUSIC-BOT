from __future__ import annotations

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from bot.constants import RATE_LIMIT_PLAY_SECONDS
from bot.utils.formatters import track_line
from bot.utils.validators import is_valid_url, validate_query


async def play_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    s = context.bot_data["services"]
    msg = update.effective_message
    chat = update.effective_chat
    user = update.effective_user
    if not msg or not chat or not user:
        return
    if not s["cooldown"].allow(chat.id, user.id, "play", RATE_LIMIT_PLAY_SECONDS):
        await msg.reply_text("⏱ Please wait before another /play request.")
        return
    query = " ".join(context.args)
    try:
        query = validate_query(query)
    except ValueError as exc:
        await msg.reply_text(str(exc))
        return
    settings = await s["settings"].get(chat.id)
    await s["repo"].upsert_chat(chat.id, chat.title, chat.type)
    await s["repo"].log_command("play", chat.id, user.id)
    if is_valid_url(query) and not settings.allow_url_mode:
        await msg.reply_text("URL mode is disabled in this chat.")
        return
    wait = await msg.reply_text("🔎 Searching…")
    try:
        if is_valid_url(query):
            track = await s["extractor"].extract(query, user.id, user.full_name)
            item = await s["queue"].enqueue(chat.id, track, settings.max_queue_length)
            await s["repo"].increment_stat("tracks_queued")
            await wait.edit_text(f"✅ Queued at #{item.position}\n{track_line(track)}", parse_mode="HTML")
            return
        tracks = await s["extractor"].search(query, user.id, user.full_name)
    except Exception as exc:  # noqa: BLE001
        await s["repo"].increment_stat("failed_extraction")
        await wait.edit_text(f"❌ Could not process request: {exc}")
        return
    rows = []
    signer = s["signer"]
    for idx, t in enumerate(tracks[:5]):
        payload = signer.sign(f"pick:{chat.id}:{user.id}:{idx}:{t.webpage_url}")
        rows.append([InlineKeyboardButton(f"{idx+1}. {t.title[:40]}", callback_data=payload)])
    await wait.edit_text("Select a track:", reply_markup=InlineKeyboardMarkup(rows))
