from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from telegram import Update
    from telegram.ext import ContextTypes


def is_global_admin(user_id: int, admin_ids: set[int]) -> bool:
    return user_id in admin_ids


async def is_chat_admin(update: "Update", context: "ContextTypes.DEFAULT_TYPE") -> bool:
    from telegram import ChatMemberAdministrator, ChatMemberOwner

    if update.effective_chat is None or update.effective_user is None:
        return False
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    member = await context.bot.get_chat_member(chat_id, user_id)
    return isinstance(member, (ChatMemberAdministrator, ChatMemberOwner))
