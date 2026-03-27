from __future__ import annotations

import aiosqlite
from pathlib import Path


class Database:
    def __init__(self, database_url: str) -> None:
        if not database_url.startswith("sqlite:///"):
            raise ValueError("Only sqlite:/// is supported currently")
        self.path = Path(database_url.replace("sqlite:///", "", 1)).resolve()

    async def connect(self) -> aiosqlite.Connection:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        conn = await aiosqlite.connect(str(self.path))
        conn.row_factory = aiosqlite.Row
        await conn.execute("PRAGMA foreign_keys = ON")
        return conn


async def init_schema(conn: aiosqlite.Connection, schema_path: Path) -> None:
    schema_sql = schema_path.read_text(encoding="utf-8")
    await conn.executescript(schema_sql)
    await conn.commit()
