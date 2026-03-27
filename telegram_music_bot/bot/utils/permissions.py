from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from telegram import Update
    from telegram.ext import ContextTypes


def is_global_admin(user_id: int, admin_ids: set[int]) -> bool:
    return user_id in admin_ids


async def is_chat_admin(update: "Update", context: "ContextTypes.DEFAULT_TYPE") -> bool:
    if not update.effective_chat or not update.effective_user:
        return False
    member = await context.bot.get_chat_member(update.effective_chat.id, update.effective_user.id)
    return getattr(member, "status", "") in {"administrator", "creator"}
