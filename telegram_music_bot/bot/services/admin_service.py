from __future__ import annotations

from bot.models import AdminAuditEntry
from bot.storage.repositories import Repository
from bot.utils.time_utils import utcnow


class AdminService:
    def __init__(self, repo: Repository, admin_ids: set[int]) -> None:
        self.repo = repo
        self.admin_ids = admin_ids

    def ensure_admin(self, user_id: int) -> None:
        if user_id not in self.admin_ids:
            raise PermissionError("Admin only")

    async def audit(self, admin_user_id: int, action: str, target: str | None, details: str | None) -> None:
        await self.repo.add_admin_audit(AdminAuditEntry(None, admin_user_id, action, target, details, utcnow()))
