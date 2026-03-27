from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
import os


@dataclass(slots=True)
class Config:
    bot_token: str
    admin_ids: set[int]
    database_url: str
    download_dir: Path
    max_track_duration_seconds: int
    max_file_size_mb: int
    default_volume: int
    maintenance_mode: bool
    log_level: str
    youtube_api_key: Optional[str] = None
    spotify_client_id: Optional[str] = None
    spotify_client_secret: Optional[str] = None
    deezer_app_id: Optional[str] = None
    deezer_app_secret: Optional[str] = None
    lastfm_api_key: Optional[str] = None
    genius_access_token: Optional[str] = None
    sentry_dsn: Optional[str] = None
    redis_url: Optional[str] = None
    webhook_url: Optional[str] = None
    webhook_secret: Optional[str] = None
    metrics_enabled: bool = False


def _bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name, str(default).lower()).strip().lower()
    return value in {"1", "true", "yes", "on"}


def load_config() -> Config:
    load_dotenv()
    admin_raw = os.getenv("ADMIN_IDS", "")
    admin_ids: set[int] = set()
    if admin_raw.strip():
        try:
            admin_ids = {int(x.strip()) for x in admin_raw.split(",") if x.strip()}
        except ValueError as exc:
            raise ValueError("ADMIN_IDS must be comma-separated integers") from exc

    token = os.getenv("BOT_TOKEN", "").strip()
    if not token:
        raise ValueError("BOT_TOKEN is required")

    cfg = Config(
        bot_token=token,
        admin_ids=admin_ids,
        database_url=os.getenv("DATABASE_URL", "sqlite:///bot.db").strip(),
        download_dir=Path(os.getenv("DOWNLOAD_DIR", "./tmp")).resolve(),
        max_track_duration_seconds=int(os.getenv("MAX_TRACK_DURATION_SECONDS", "1800")),
        max_file_size_mb=int(os.getenv("MAX_FILE_SIZE_MB", "100")),
        default_volume=int(os.getenv("DEFAULT_VOLUME", "100")),
        maintenance_mode=_bool("MAINTENANCE_MODE", False),
        log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
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
        metrics_enabled=_bool("METRICS_ENABLED", False),
    )
    if not (1 <= cfg.default_volume <= 100):
        raise ValueError("DEFAULT_VOLUME must be 1..100")
    return cfg
