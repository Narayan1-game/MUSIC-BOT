from __future__ import annotations

import asyncio
import shutil


class FFmpegService:
    async def ensure_available(self) -> None:
        if shutil.which("ffmpeg") is None:
            raise RuntimeError("ffmpeg binary not found in PATH")

    async def run_probe(self, media_path: str) -> int:
        proc = await asyncio.create_subprocess_exec(
            "ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", media_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        try:
            stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=10)
        except TimeoutError:
            proc.kill()
            await proc.wait()
            raise
        if proc.returncode != 0:
            return 0
        try:
            return int(float(stdout.decode().strip()))
        except ValueError:
            return 0
