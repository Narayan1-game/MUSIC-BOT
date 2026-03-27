from __future__ import annotations


class HealthService:
    async def ping(self) -> str:
        return "pong"
