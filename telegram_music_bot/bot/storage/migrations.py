from __future__ import annotations

from pathlib import Path

from bot.db import init_schema


async def run_migrations(conn, schema_path: Path) -> None:
    await init_schema(conn, schema_path)
