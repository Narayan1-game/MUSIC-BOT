from __future__ import annotations

from pathlib import Path
import re
import uuid


_SAFE = re.compile(r"[^a-zA-Z0-9._-]+")


def sanitize_filename(name: str) -> str:
    cleaned = _SAFE.sub("_", name).strip("._")
    return cleaned[:120] or "track"


def unique_temp_path(base_dir: Path, suffix: str = ".tmp") -> Path:
    base_dir.mkdir(parents=True, exist_ok=True)
    return base_dir / f"{uuid.uuid4().hex}{suffix}"
