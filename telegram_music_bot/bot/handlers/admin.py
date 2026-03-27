from __future__ import annotations

import asyncio

from telegram import Update
from telegram.ext import ContextTypes

from bot.utils.formatters import format_stats


async def _ensure(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    s = context.bot_data["services"]
    user_id = update.effective_user.id
    try:
        s["admin"].ensure_admin(user_id)
        return True
    except PermissionError:
        await update.effective_message.reply_text("Admin only.")
        return False


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _ensure(update, context):
        return
    s = context.bot_data["services"]
    snapshot = await s["stats"].snapshot()
    top = await s["repo"].top_commands()
    await update.effective_message.reply_text(format_stats(snapshot, top), parse_mode="HTML")


async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _ensure(update, context):
        return
    s = context.bot_data["services"]
    message = " ".join(context.args).strip()
    if not message:
        await update.effective_message.reply_text("Usage: /broadcast <message>")
        return
    rows = await (await s["repo"].conn.execute("SELECT chat_id FROM chats")).fetchall()
    ok = 0
    fail = 0
    for row in rows:
        try:
            await context.bot.send_message(chat_id=row["chat_id"], text=message)
            ok += 1
            await asyncio.sleep(0.05)
        except Exception:
            fail += 1
    await s["admin"].audit(update.effective_user.id, "broadcast", None, f"ok={ok},fail={fail}")
    await update.effective_message.reply_text(f"Broadcast done. Sent: {ok}, failed: {fail}")


async def maintenance_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _ensure(update, context):
        return
    arg = (context.args[0] if context.args else "").lower()
    context.bot_data["maintenance"] = arg == "on"
    await context.bot_data["services"]["admin"].audit(update.effective_user.id, "maintenance", None, arg)
    await update.effective_message.reply_text(f"Maintenance: {arg}")


async def auditlog_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _ensure(update, context):
        return
    rows = await context.bot_data["services"]["repo"].latest_audit(15)
    text = "\n".join(f"{r['created_at']} {r['action']} {r['details'] or ''}" for r in rows) or "No entries"
    await update.effective_message.reply_text(text[:3500])


async def generic_admin_noop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await _ensure(update, context):
        return
    await update.effective_message.reply_text("Command accepted (placeholder).")
