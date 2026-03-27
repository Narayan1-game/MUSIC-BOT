from __future__ import annotations

import asyncio


class FFmpegService:
    async def check_binary(self) -> bool:
        proc = await asyncio.create_subprocess_exec("ffmpeg", "-version", stdout=asyncio.subprocess.DEVNULL, stderr=asyncio.subprocess.DEVNULL)
        return (await proc.wait()) == 0
