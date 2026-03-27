from __future__ import annotations

from html import escape

from bot.models import BotHealthSnapshot, ChatSettings, PlaybackState, QueueItem, Track


def track_line(track: Track) -> str:
    duration = f"{track.duration_seconds}s" if track.duration_seconds else "Live/Unknown"
    return f"<b>{escape(track.title)}</b> • {duration} • by {escape(track.requested_by_name)}"


def format_queue(current: QueueItem | None, upcoming: list[QueueItem], page: int, pages: int, repeat_mode: str) -> str:
    lines = [f"🎵 <b>Queue</b> • Repeat: <code>{escape(repeat_mode)}</code> • Page {page}/{pages}"]
    if current:
        lines.append(f"Now: {track_line(current.track)}")
    if not upcoming:
        lines.append("No upcoming tracks.")
    else:
        for item in upcoming:
            lines.append(f"{item.position}. {track_line(item.track)}")
    return "\n".join(lines)


def format_now_playing(item: QueueItem | None, state: PlaybackState | None) -> str:
    if not item or not state:
        return "Nothing is currently active."
    return f"▶️ <b>Now Playing</b>\n{track_line(item.track)}\nState: <code>{state.state}</code>"


def format_settings(settings: ChatSettings) -> str:
    return (
        "⚙️ <b>Settings</b>\n"
        f"Admin-only mode: <b>{settings.admin_only_mode}</b>\n"
        f"Allow URLs: <b>{settings.allow_url_mode}</b>\n"
        f"Autoplay: <b>{settings.autoplay_enabled}</b>\n"
        f"Queue limit: <b>{settings.max_queue_length}</b>\n"
        f"Default volume: <b>{settings.default_volume}</b>"
    )


def format_stats(snapshot: BotHealthSnapshot, top_commands: list[tuple[str, int]]) -> str:
    cmd_lines = "\n".join(f"• {escape(name)}: {count}" for name, count in top_commands) or "No usage yet"
    return (
        "📊 <b>Bot Stats</b>\n"
        f"Uptime: <b>{snapshot.uptime_seconds}s</b>\n"
        f"Chats: <b>{snapshot.total_chats}</b> | Users: <b>{snapshot.total_users_seen}</b>\n"
        f"Queued: <b>{snapshot.total_tracks_queued}</b> | Played: <b>{snapshot.total_tracks_played}</b>\n"
        f"Failures (extract/play): <b>{snapshot.failed_extraction_count}/{snapshot.failed_playback_count}</b>\n"
        f"Top commands:\n{cmd_lines}"
    )
