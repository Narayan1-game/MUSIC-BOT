from __future__ import annotations

import logging
import os
import time
from pathlib import Path


class CleanupService:
    def __init__(self, download_dir: Path, max_age_seconds: int = 3600) -> None:
        self.download_dir = download_dir
        self.max_age_seconds = max_age_seconds
        self.log = logging.getLogger(__name__)

    async def run_once(self) -> int:
        if not self.download_dir.exists():
            return 0
        now = time.time()
        removed = 0
        for entry in self.download_dir.iterdir():
            try:
                if entry.is_file() and now - entry.stat().st_mtime > self.max_age_seconds:
                    os.remove(entry)
                    removed += 1
            except OSError:
                continue
        self.log.info("cleanup_run", extra={"removed": removed})
        return removed
