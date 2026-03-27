# Telegram Music Bot (Production-Ready Foundation)

## Features
- Async python-telegram-bot architecture with dependency wiring.
- Per-chat persistent queue and playback state.
- Provider router with yt-dlp default fallback.
- Signed callback payloads and SSRF-safe URL validation.
- Admin tools, stats, audit log, throttling, cleanup jobs.

## Setup
```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp sample.env .env
# Fill .env values
python -m bot.main
```

## FFmpeg install
```bash
sudo apt update
sudo apt install -y ffmpeg
```

## Ubuntu VPS deployment
1. Create system user and clone repository.
2. Configure `.env`.
3. Install dependencies in venv.
4. Install systemd unit.

## systemd
```bash
sudo cp musicbot.service /etc/systemd/system/musicbot.service
sudo systemctl daemon-reload
sudo systemctl enable --now musicbot
sudo systemctl status musicbot
```

## Environment variables
Required:
- `BOT_TOKEN`
- `ADMIN_IDS`
- `DATABASE_URL`
- `DOWNLOAD_DIR`
- `MAX_TRACK_DURATION_SECONDS`
- `MAX_FILE_SIZE_MB`
- `DEFAULT_VOLUME`
- `MAINTENANCE_MODE`
- `LOG_LEVEL`

Optional: YouTube API, Spotify, Deezer, LastFM, Genius, Sentry, Redis, webhook, metrics.

## Troubleshooting
- Startup fails with ffmpeg missing: install ffmpeg.
- DB issues: verify `DATABASE_URL=sqlite:///...` is writable.
- Callback invalid: ensure `WEBHOOK_SECRET` is stable.

## Command reference
`/start /help /play /search /queue /nowplaying /skip /pause /resume /stop /clear /remove /shuffle /repeat /volume /settings /lyrics /history /import /ping /stats /broadcast /maintenance /auditlog`

## Known limitations and next upgrade steps
- Placeholder integrations for Spotify/Deezer/LastFM/Genius.
- Current player state logic is backend-ready; real voice chat streaming backend should be added as next step.
- Add PostgreSQL repository implementation.
- Add Redis-backed distributed rate limiting.
- Add webhook deployment profile.
