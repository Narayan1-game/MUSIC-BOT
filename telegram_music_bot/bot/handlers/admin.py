from __future__ import annotations

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes


def require_services(context: ContextTypes.DEFAULT_TYPE):
    return context.application.bot_data["services"]


from bot.utils.permissions import is_global_admin


def _guard(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    user = update.effective_user
    admins = context.application.bot_data["config"].admin_ids
    return bool(user and is_global_admin(user.id, admins))


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _guard(update, context):
        await update.effective_message.reply_text("Admin only.")
        return
    s = await require_services(context)["stats"].snapshot()
    text = (
        f"<b>Stats</b>
Uptime: {s.uptime_seconds}s
Chats: {s.total_chats}
Users: {s.total_users}
"
        f"Queued: {s.total_tracks_queued}
Played: {s.total_tracks_played}"
    )
    await update.effective_message.reply_text(text, parse_mode="HTML")


async def maintenance_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _guard(update, context):
        await update.effective_message.reply_text("Admin only.")
        return
    arg = (context.args[0].lower() if context.args else "")
    if arg not in {"on", "off"}:
        await update.effective_message.reply_text("Usage: /maintenance on|off")
        return
    context.application.bot_data["config"].maintenance_mode = arg == "on"
    await require_services(context)["admin"].audit(update.effective_user.id, "maintenance", "bot", "maintenance_mode", arg)
    await update.effective_message.reply_text(f"Maintenance mode: {arg}")


async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _guard(update, context):
        await update.effective_message.reply_text("Admin only.")
        return
    msg = " ".join(context.args).strip()
    if not msg:
        await update.effective_message.reply_text("Usage: /broadcast <message>")
        return
    repo = require_services(context)["repo"]
    rows = await repo.conn.execute_fetchall("SELECT id FROM chats")
    ok = 0
    fail = 0
    for r in rows:
        try:
            await context.bot.send_message(chat_id=r["id"], text=msg)
            ok += 1
        except Exception:
            fail += 1
    await update.effective_message.reply_text(f"Broadcast complete. delivered={ok}, failed={fail}")


async def banuser_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _guard(update, context):
        await update.effective_message.reply_text("Admin only.")
        return
    if not context.args or not context.args[0].isdigit():
        await update.effective_message.reply_text("Usage: /banuser <user_id>")
        return
    uid = int(context.args[0])
    await require_services(context)["repo"].conn.execute("INSERT OR IGNORE INTO banned_users(user_id,reason,created_at) VALUES(?,?,datetime('now'))", (uid, "manual"))
    await require_services(context)["repo"].conn.commit()
    await update.effective_message.reply_text(f"User {uid} banned.")


async def unbanuser_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _guard(update, context):
        await update.effective_message.reply_text("Admin only.")
        return
    if not context.args or not context.args[0].isdigit():
        await update.effective_message.reply_text("Usage: /unbanuser <user_id>")
        return
    uid = int(context.args[0])
    await require_services(context)["repo"].conn.execute("DELETE FROM banned_users WHERE user_id=?", (uid,))
    await require_services(context)["repo"].conn.commit()
    await update.effective_message.reply_text(f"User {uid} unbanned.")


async def admins_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _guard(update, context):
        await update.effective_message.reply_text("Admin only.")
        return
    admins = sorted(context.application.bot_data["config"].admin_ids)
    await update.effective_message.reply_text("Admins: " + ", ".join(map(str, admins)))


async def reloadconfig_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _guard(update, context):
        await update.effective_message.reply_text("Admin only.")
        return
    await update.effective_message.reply_text("Config reload placeholder ready.")


async def auditlog_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _guard(update, context):
        await update.effective_message.reply_text("Admin only.")
        return
    rows = await require_services(context)["admin"].recent_audit()
    if not rows:
        await update.effective_message.reply_text("No audit records.")
        return
    text = "
".join(f"{r['created_at']} • {r['action']} • {r.get('target_id') or '-'}" for r in rows[:10])
    await update.effective_message.reply_text(text)


async def setdefaultvolume_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _guard(update, context):
        await update.effective_message.reply_text("Admin only.")
        return
    if not context.args or not context.args[0].isdigit():
        await update.effective_message.reply_text("Usage: /setdefaultvolume <1-100>")
        return
    value = int(context.args[0])
    if value < 1 or value > 100:
        await update.effective_message.reply_text("Volume must be 1..100")
        return
    settings = await require_services(context)["settings"].get(update.effective_chat.id)
    settings.default_volume = value
    await require_services(context)["repo"].save_settings(settings)
    await update.effective_message.reply_text(f"Default volume set to {value}%")


async def blacklistchat_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _guard(update, context):
        await update.effective_message.reply_text("Admin only.")
        return
    if not context.args or not context.args[0].isdigit():
        await update.effective_message.reply_text("Usage: /blacklistchat <chat_id>")
        return
    cid = int(context.args[0])
    await require_services(context)["repo"].conn.execute("INSERT OR IGNORE INTO blacklisted_chats(chat_id,reason,created_at) VALUES(?,?,datetime('now'))", (cid, "manual"))
    await require_services(context)["repo"].conn.commit()
    await update.effective_message.reply_text(f"Chat {cid} blacklisted.")


async def unblacklistchat_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _guard(update, context):
        await update.effective_message.reply_text("Admin only.")
        return
    if not context.args or not context.args[0].isdigit():
        await update.effective_message.reply_text("Usage: /unblacklistchat <chat_id>")
        return
    cid = int(context.args[0])
    await require_services(context)["repo"].conn.execute("DELETE FROM blacklisted_chats WHERE chat_id=?", (cid,))
    await require_services(context)["repo"].conn.commit()
    await update.effective_message.reply_text(f"Chat {cid} removed from blacklist.")
