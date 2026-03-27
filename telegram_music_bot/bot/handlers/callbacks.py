from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from bot.utils.pagination import paginate


async def callback_router(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query:
        return
    s = context.bot_data["services"]
    try:
        payload = s["signer"].verify(query.data)
    except Exception:
        await query.answer("Invalid action", show_alert=True)
        return

    parts = payload.split(":", 4)
    action = parts[0]
    chat_id = int(parts[1]) if len(parts) > 1 and parts[1].lstrip("-").isdigit() else None
    if chat_id != update.effective_chat.id:
        await query.answer("Wrong chat", show_alert=True)
        return

    if action == "pick":
        _, _, user_id, _, url = parts
        if int(user_id) != update.effective_user.id:
            await query.answer("Only requester can select.", show_alert=True)
            return
        track = await s["extractor"].extract(url, update.effective_user.id, update.effective_user.full_name)
        settings = await s["settings"].get(chat_id)
        item = await s["queue"].enqueue(chat_id, track, settings.max_queue_length)
        await s["repo"].increment_stat("tracks_queued")
        await query.edit_message_text(f"✅ Queued #{item.position}: {track.title}")
    elif action == "set":
        _, _, field = parts[:3]
        settings = await s["settings"].toggle(chat_id, field)
        await query.edit_message_text(f"Updated {field}: {getattr(settings, field)}")
    elif action == "q":
        _, _, p = parts
        items = await s["queue"].get_queue(chat_id)
        chunk, page, pages = paginate(items, int(p), 10)
        lines = [f"Queue page {page}/{pages}"] + [f"{i.position}. {i.track.title}" for i in chunk]
        await query.edit_message_text("\n".join(lines))
    elif action == "ctl":
        _, _, ctl = parts
        if ctl == "skip":
            await context.bot_data["services"]["queue"].pop_next(chat_id)
        await query.answer("Done")
    elif action == "nav":
        await query.answer("Use command panel")
    else:
        await query.answer("Unknown action")
