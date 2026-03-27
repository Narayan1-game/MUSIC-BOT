from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


@dataclass(slots=True)
class BotConfig:
    bot_token: str
    admin_ids: set[int]
    database_url: str
    download_dir: Path
    max_track_duration_seconds: int
    max_file_size_mb: int
    default_volume: int
    maintenance_mode: bool
    log_level: str
    youtube_api_key: str | None
    spotify_client_id: str | None
    spotify_client_secret: str | None
    deezer_app_id: str | None
    deezer_app_secret: str | None
    lastfm_api_key: str | None
    genius_access_token: str | None
    sentry_dsn: str | None
    redis_url: str | None
    webhook_url: str | None
    webhook_secret: str | None
    metrics_enabled: bool


def _parse_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _parse_admin_ids(raw: str) -> set[int]:
    ids: set[int] = set()
    for item in raw.split(","):
        value = item.strip()
        if not value:
            continue
        if not value.lstrip("-").isdigit():
            raise ValueError(f"Invalid ADMIN_IDS entry: {value}")
        ids.add(int(value))
    return ids


def load_config() -> BotConfig:
    load_dotenv()
    token = os.getenv("BOT_TOKEN", "").strip()
    if not token:
        raise ValueError("BOT_TOKEN is required")
    admin_ids = _parse_admin_ids(os.getenv("ADMIN_IDS", ""))
    if not admin_ids:
        raise ValueError("ADMIN_IDS must include at least one numeric id")

    download_dir = Path(os.getenv("DOWNLOAD_DIR", "./tmp")).resolve()

    return BotConfig(
        bot_token=token,
        admin_ids=admin_ids,
        database_url=os.getenv("DATABASE_URL", "sqlite:///bot.db"),
        download_dir=download_dir,
        max_track_duration_seconds=int(os.getenv("MAX_TRACK_DURATION_SECONDS", "1800")),
        max_file_size_mb=int(os.getenv("MAX_FILE_SIZE_MB", "100")),
        default_volume=int(os.getenv("DEFAULT_VOLUME", "100")),
        maintenance_mode=_parse_bool(os.getenv("MAINTENANCE_MODE"), False),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        youtube_api_key=os.getenv("YOUTUBE_API_KEY") or None,
        spotify_client_id=os.getenv("SPOTIFY_CLIENT_ID") or None,
        spotify_client_secret=os.getenv("SPOTIFY_CLIENT_SECRET") or None,
        deezer_app_id=os.getenv("DEEZER_APP_ID") or None,
        deezer_app_secret=os.getenv("DEEZER_APP_SECRET") or None,
        lastfm_api_key=os.getenv("LASTFM_API_KEY") or None,
        genius_access_token=os.getenv("GENIUS_ACCESS_TOKEN") or None,
        sentry_dsn=os.getenv("SENTRY_DSN") or None,
        redis_url=os.getenv("REDIS_URL") or None,
        webhook_url=os.getenv("WEBHOOK_URL") or None,
        webhook_secret=os.getenv("WEBHOOK_SECRET") or None,
        metrics_enabled=_parse_bool(os.getenv("METRICS_ENABLED"), False),
    )
