from __future__ import annotations

import aiosqlite
from pathlib import Path


class Database:
    def __init__(self, database_url: str, schema_path: Path) -> None:
        if not database_url.startswith("sqlite:///"):
            raise ValueError("Only sqlite:/// URLs are supported for now")
        self.db_path = Path(database_url.replace("sqlite:///", "", 1)).resolve()
        self.schema_path = schema_path

    async def connect(self) -> aiosqlite.Connection:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = await aiosqlite.connect(self.db_path)
        conn.row_factory = aiosqlite.Row
        await conn.execute("PRAGMA foreign_keys=ON")
        return conn

    async def initialize(self) -> None:
        async with await self.connect() as conn:
            schema = self.schema_path.read_text(encoding="utf-8")
            await conn.executescript(schema)
            await conn.commit()
