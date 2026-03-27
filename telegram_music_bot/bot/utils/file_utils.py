from __future__ import annotations

import re
import uuid
from pathlib import Path


def safe_filename(name: str, ext: str = ".tmp") -> str:
    slug = re.sub(r"[^a-zA-Z0-9._-]", "_", name)[:40]
    return f"{slug}_{uuid.uuid4().hex}{ext}"


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
