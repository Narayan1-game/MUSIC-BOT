# Telegram Music Bot (Production-Oriented)

Premium async Telegram music bot for Python 3.11 with queue persistence, modular architecture, and secure defaults.

## Features
- Per-chat queues with locking and persistence.
- /play, /search, /queue, /nowplaying, playback controls.
- Admin controls: stats, broadcast, maintenance, ban/blacklist tools.
- Signed callback data and per-user cooldowns.
- SQLite default via aiosqlite; repository abstraction for PostgreSQL later.
- Polling by default, webhook-ready configuration.

## Project Tree
```text
telegram_music_bot/
  bot/
    main.py
    config.py
    constants.py
    db.py
    models.py
    logging_setup.py
    handlers/
    services/
    providers/
    storage/
    utils/
  tests/
  requirements.txt
  sample.env
  README.md
  musicbot.service
```

## Setup
```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp sample.env .env
# fill .env
python -m bot.main
```

## FFmpeg install (Ubuntu)
```bash
sudo apt update
sudo apt install -y ffmpeg
```

## Ubuntu VPS deployment
1. Copy project to `/opt/telegram_music_bot`.
2. Create virtualenv and install requirements.
3. Configure `.env`.
4. Install systemd service from `musicbot.service`.
5. Enable service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now musicbot
sudo systemctl status musicbot
```

## Environment Variables
Required: `BOT_TOKEN`, `ADMIN_IDS`, `DATABASE_URL`, `DOWNLOAD_DIR`, `MAX_TRACK_DURATION_SECONDS`, `MAX_FILE_SIZE_MB`, `DEFAULT_VOLUME`, `MAINTENANCE_MODE`, `LOG_LEVEL`.

Optional: `YOUTUBE_API_KEY`, `SPOTIFY_CLIENT_ID`, `SPOTIFY_CLIENT_SECRET`, `DEEZER_APP_ID`, `DEEZER_APP_SECRET`, `LASTFM_API_KEY`, `GENIUS_ACCESS_TOKEN`, `SENTRY_DSN`, `REDIS_URL`, `WEBHOOK_URL`, `WEBHOOK_SECRET`, `METRICS_ENABLED`.

## Command Reference
General: `/start /help /ping`
Playback: `/play /pause /resume /skip /stop /nowplaying /volume`
Queue: `/queue /clear /remove /shuffle /repeat`
Settings: `/settings`
Admin: `/stats /broadcast /maintenance /banuser /unbanuser /admins /auditlog /blacklistchat /unblacklistchat`

## Troubleshooting
- `ffmpeg not found`: install ffmpeg and restart.
- DB path errors: verify `DATABASE_URL=sqlite:///...` and write permissions.
- No extraction results: verify network egress and yt-dlp availability.

## Known limitations and next upgrade steps
- Playback is stateful/control-ready; real Telegram voice chat streaming backend is intentionally isolated for future plugin integration.
- Redis and Sentry are capability hooks; add concrete adapters as next step.
- PostgreSQL backend can be added by implementing repository interface.
- Playlist / import providers are scaffolded and ready for extension.
