from __future__ import annotations

from bot.models import AdminAuditEntry
from bot.storage.repositories import Repository


class AdminService:
    def __init__(self, repo: Repository) -> None:
        self.repo = repo

    async def audit(self, admin_id: int, action: str, target_type: str | None = None, target_id: str | None = None, details: str | None = None) -> None:
        await self.repo.add_audit_entry(AdminAuditEntry(admin_user_id=admin_id, action=action, target_type=target_type, target_id=target_id, details=details))

    async def recent_audit(self) -> list[dict]:
        return await self.repo.get_audit_entries()
