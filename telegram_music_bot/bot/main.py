from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from telegram.ext import Application, ApplicationBuilder, CallbackQueryHandler, CommandHandler

from bot.config import BotConfig, load_config
from bot.db import Database
from bot.handlers.admin import (
    auditlog_command,
    broadcast_command,
    generic_admin_noop,
    maintenance_command,
    stats_command,
)
from bot.handlers.callbacks import callback_router
from bot.handlers.errors import error_handler
from bot.handlers.help import help_command
from bot.handlers.history import history_command
from bot.handlers.lyrics import lyrics_command
from bot.handlers.misc import import_command, ping_command
from bot.handlers.play import play_command
from bot.handlers.playback import (
    clear_command,
    nowplaying_command,
    pause_command,
    remove_command,
    repeat_command,
    resume_command,
    shuffle_command,
    skip_command,
    stop_command,
    volume_command,
)
from bot.handlers.queue import queue_command
from bot.handlers.search import search_command
from bot.handlers.settings import settings_command
from bot.handlers.start import start_command
from bot.logging_setup import setup_logging
from bot.providers.lyrics_provider import LyricsProvider
from bot.providers.yt_dlp_provider import YtDlpProvider
from bot.services.admin_service import AdminService
from bot.services.cleanup_service import CleanupService
from bot.services.extractor_service import ExtractorService
from bot.services.ffmpeg_service import FFmpegService
from bot.services.health_service import HealthService
from bot.services.history_service import HistoryService
from bot.services.lyrics_service import LyricsService
from bot.services.player_service import PlayerService
from bot.services.provider_router import ProviderRouter
from bot.services.queue_service import QueueService
from bot.services.settings_service import SettingsService
from bot.services.stats_service import StatsService
from bot.storage.migrations import run_migrations
from bot.storage.repositories import Repository
from bot.utils.callback_data import CallbackSigner
from bot.utils.file_utils import ensure_dir
from bot.utils.throttling import CooldownManager

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class ServiceContainer:
    repo: Repository
    settings: SettingsService
    queue: QueueService
    player: PlayerService
    extractor: ExtractorService
    admin: AdminService
    stats: StatsService
    history: HistoryService
    lyrics: LyricsService
    health: HealthService
    cleanup: CleanupService
    cooldown: CooldownManager
    signer: CallbackSigner

    def as_dict(self) -> dict[str, object]:
        return self.__dict__.copy()


async def _cleanup_job(context):
    removed = await context.application.bot_data["services"]["cleanup"].sweep()
    if removed:
        logger.info("cleanup removed files=%s", removed)


def validate_startup(config: BotConfig, ffmpeg_ok: bool) -> None:
    if not ffmpeg_ok:
        raise RuntimeError("ffmpeg binary not found")
    ensure_dir(config.download_dir)
    test_file = config.download_dir / ".writable"
    test_file.write_text("ok", encoding="utf-8")
    test_file.unlink(missing_ok=True)


async def build_application() -> Application:
    config = load_config()
    setup_logging(config.log_level)
    db = Database(config.database_url)
    conn = await db.connect()
    await run_migrations(conn, Path(__file__).parent / "storage" / "schema.sql")
    repo = Repository(conn)
    ffmpeg_service = FFmpegService()
    validate_startup(config, await ffmpeg_service.check_binary())

    providers = [YtDlpProvider()]
    router = ProviderRouter(providers)

    services = ServiceContainer(
        repo=repo,
        settings=SettingsService(repo, config.default_volume),
        queue=QueueService(repo),
        player=PlayerService(repo, config.default_volume),
        extractor=ExtractorService(router),
        admin=AdminService(repo, config.admin_ids),
        stats=StatsService(repo, datetime.utcnow(), {"yt_dlp": True, "redis": bool(config.redis_url), "sentry": bool(config.sentry_dsn)}),
        history=HistoryService(repo),
        lyrics=LyricsService(LyricsProvider()),
        health=HealthService(),
        cleanup=CleanupService(config.download_dir),
        cooldown=CooldownManager(),
        signer=CallbackSigner(config.webhook_secret or config.bot_token[:16]),
    )

    app = ApplicationBuilder().token(config.bot_token).build()
    app.bot_data["services"] = services.as_dict()
    app.bot_data["maintenance"] = config.maintenance_mode

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("play", play_command))
    app.add_handler(CommandHandler("search", search_command))
    app.add_handler(CommandHandler("queue", queue_command))
    app.add_handler(CommandHandler("nowplaying", nowplaying_command))
    app.add_handler(CommandHandler("skip", skip_command))
    app.add_handler(CommandHandler("pause", pause_command))
    app.add_handler(CommandHandler("resume", resume_command))
    app.add_handler(CommandHandler("stop", stop_command))
    app.add_handler(CommandHandler("clear", clear_command))
    app.add_handler(CommandHandler("remove", remove_command))
    app.add_handler(CommandHandler("shuffle", shuffle_command))
    app.add_handler(CommandHandler("repeat", repeat_command))
    app.add_handler(CommandHandler("volume", volume_command))
    app.add_handler(CommandHandler("settings", settings_command))
    app.add_handler(CommandHandler("lyrics", lyrics_command))
    app.add_handler(CommandHandler("history", history_command))
    app.add_handler(CommandHandler("import", import_command))
    app.add_handler(CommandHandler("ping", ping_command))

    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(CommandHandler("broadcast", broadcast_command))
    app.add_handler(CommandHandler("banuser", generic_admin_noop))
    app.add_handler(CommandHandler("unbanuser", generic_admin_noop))
    app.add_handler(CommandHandler("maintenance", maintenance_command))
    app.add_handler(CommandHandler("admins", generic_admin_noop))
    app.add_handler(CommandHandler("reloadconfig", generic_admin_noop))
    app.add_handler(CommandHandler("auditlog", auditlog_command))
    app.add_handler(CommandHandler("setdefaultvolume", generic_admin_noop))
    app.add_handler(CommandHandler("blacklistchat", generic_admin_noop))
    app.add_handler(CommandHandler("unblacklistchat", generic_admin_noop))

    app.add_handler(CallbackQueryHandler(callback_router))
    app.add_error_handler(error_handler)

    app.job_queue.run_repeating(_cleanup_job, interval=600, first=600)
    return app


def main() -> None:
    async def runner() -> None:
        app = await build_application()
        await app.initialize()
        await app.start()
        await app.updater.start_polling()
        try:
            while True:
                await asyncio.sleep(60)
        finally:
            await app.updater.stop()
            await app.stop()
            await app.shutdown()

    asyncio.run(runner())


if __name__ == "__main__":
    main()
