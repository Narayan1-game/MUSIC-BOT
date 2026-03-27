from __future__ import annotations

import logging
import secrets
import time

from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler

from bot.config import load_config
from bot.db import Database
from bot.handlers.admin import (admins_command, auditlog_command, banuser_command,
                                blacklistchat_command, broadcast_command,
                                maintenance_command, reloadconfig_command,
                                setdefaultvolume_command, stats_command,
                                unbanuser_command, unblacklistchat_command)
from bot.handlers.callbacks import callback_handler
from bot.handlers.errors import error_handler
from bot.handlers.help import help_command
from bot.handlers.history import history_command
from bot.handlers.lyrics import lyrics_command
from bot.handlers.play import play_command
from bot.handlers.playback import (clear_command, nowplaying_command, pause_command,
                                   remove_command, repeat_command, resume_command,
                                   shuffle_command, skip_command, stop_command,
                                   volume_command)
from bot.handlers.queue import queue_command
from bot.handlers.search import search_command
from bot.handlers.settings import settings_command
from bot.handlers.start import start_command
from bot.logging_setup import setup_logging
from bot.providers.lyrics_provider import LyricsProvider
from bot.providers.yt_dlp_provider import YtDlpProvider
from bot.services.cleanup_service import CleanupService
from bot.services.admin_service import AdminService
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
from bot.storage.repositories import Repository
from bot.utils.callback_data import CallbackDataCodec
from bot.utils.throttling import RateLimiter


async def _bootstrap() -> tuple:
    config = load_config()
    setup_logging(config.log_level)
    log = logging.getLogger(__name__)
    db = Database(config.database_url, schema_path=__import__("pathlib").Path(__file__).parent / "storage" / "schema.sql")
    await db.initialize()
    conn = await db.connect()
    repo = Repository(conn)
    ffmpeg = FFmpegService()
    await ffmpeg.ensure_available()
    config.download_dir.mkdir(parents=True, exist_ok=True)
    providers = [YtDlpProvider(config.download_dir, config.max_track_duration_seconds)]
    router = ProviderRouter(providers)
    services = {
        "repo": repo,
        "rate_limiter": RateLimiter(),
        "callback_codec": CallbackDataCodec(secrets.token_hex(16)),
        "extractor": ExtractorService(router),
        "settings": SettingsService(repo),
        "queue": QueueService(repo),
        "player": PlayerService(repo),
        "lyrics": LyricsService(LyricsProvider(config.genius_access_token)),
        "admin": AdminService(repo),
        "history": HistoryService(repo),
    }
    caps = {
        "yt_dlp": True,
        "genius": bool(config.genius_access_token),
        "redis": bool(config.redis_url),
        "sentry": bool(config.sentry_dsn),
        "webhook": bool(config.webhook_url),
    }
    services["stats"] = StatsService(repo, caps, start_ts=time.time())
    services["health"] = HealthService(services["stats"])
    cleanup = CleanupService(config.download_dir)
    log.info("bootstrap_complete")
    return config, services, cleanup, conn


async def _cleanup_job(context):
    await context.application.bot_data["cleanup"].run_once()


async def ping_command(update, context):
    msg = await context.application.bot_data["services"]["health"].ping()
    await update.effective_message.reply_text(msg)


def build_application(config, services, cleanup):
    app = ApplicationBuilder().token(config.bot_token).build()
    app.bot_data["config"] = config
    app.bot_data["services"] = services
    app.bot_data["cleanup"] = cleanup

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
    app.add_handler(CommandHandler("import", lambda u, c: u.effective_message.reply_text("Import provider architecture is ready.")))
    app.add_handler(CommandHandler("ping", ping_command))

    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(CommandHandler("broadcast", broadcast_command))
    app.add_handler(CommandHandler("banuser", banuser_command))
    app.add_handler(CommandHandler("unbanuser", unbanuser_command))
    app.add_handler(CommandHandler("maintenance", maintenance_command))
    app.add_handler(CommandHandler("admins", admins_command))
    app.add_handler(CommandHandler("reloadconfig", reloadconfig_command))
    app.add_handler(CommandHandler("auditlog", auditlog_command))
    app.add_handler(CommandHandler("setdefaultvolume", setdefaultvolume_command))
    app.add_handler(CommandHandler("blacklistchat", blacklistchat_command))
    app.add_handler(CommandHandler("unblacklistchat", unblacklistchat_command))

    app.add_handler(CallbackQueryHandler(callback_handler))
    app.add_error_handler(error_handler)
    app.job_queue.run_repeating(_cleanup_job, interval=1800, first=120, name="cleanup")
    return app


async def main() -> None:
    config, services, cleanup, conn = await _bootstrap()
    app = build_application(config, services, cleanup)
    try:
        await app.initialize()
        await app.start()
        if config.webhook_url:
            await app.updater.start_webhook(listen="0.0.0.0", port=8443, webhook_url=config.webhook_url, secret_token=config.webhook_secret)
        else:
            await app.updater.start_polling(drop_pending_updates=True)
        await app.updater.idle()
    finally:
        await conn.close()
        await app.stop()
        await app.shutdown()


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
