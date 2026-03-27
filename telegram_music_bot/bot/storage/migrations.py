from __future__ import annotations

from pathlib import Path


def migration_version_file(db_path: Path) -> Path:
    return db_path.with_suffix(".version")
