from __future__ import annotations

from pathlib import Path
from time import time


class CleanupService:
    def __init__(self, directory: Path, max_age_seconds: int = 3600) -> None:
        self.directory = directory
        self.max_age_seconds = max_age_seconds

    async def sweep(self) -> int:
        removed = 0
        now = time()
        for path in self.directory.glob("*"):
            if path.is_file() and now - path.stat().st_mtime > self.max_age_seconds:
                path.unlink(missing_ok=True)
                removed += 1
        return removed
