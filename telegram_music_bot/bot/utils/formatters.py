from __future__ import annotations

from html import escape
from bot.models import ChatSettings, PlaybackState, QueueItem, Track


def safe(value: str | None) -> str:
    return escape(value or "")


def format_track_line(track: Track, index: int | None = None) -> str:
    prefix = f"{index}. " if index is not None else ""
    duration = f"{track.duration_seconds//60}:{track.duration_seconds%60:02d}" if track.duration_seconds else "LIVE"
    return f"{prefix}<b>{safe(track.title)}</b> • {duration} • by {safe(track.requested_by_name)}"


def format_queue_page(items: list[QueueItem], page: int, total_pages: int, repeat_mode: str) -> str:
    if not items:
        return "<b>Queue is empty.</b>"
    lines = [f"<b>Queue</b> • page {page}/{total_pages} • repeat: <code>{repeat_mode}</code>"]
    for item in items:
        lines.append(format_track_line(item.track, item.position))
    return "
".join(lines)


def format_now_playing(track: Track | None, state: PlaybackState | None) -> str:
    if not track or not state:
        return "<b>Nothing is currently playing.</b>"
    return (
        f"<b>Now Playing</b>
"
        f"{format_track_line(track)}
"
        f"Status: <code>{safe(state.status)}</code> • Repeat: <code>{safe(state.repeat_mode)}</code> • Volume: <code>{state.volume}%</code>"
    )


def format_settings(settings: ChatSettings) -> str:
    return (
        "<b>Chat Settings</b>
"
        f"Admin-only mode: <code>{settings.admin_only_mode}</code>
"
        f"Allow URLs: <code>{settings.allow_url_mode}</code>
"
        f"Autoplay: <code>{settings.autoplay_enabled}</code>
"
        f"Max queue length: <code>{settings.max_queue_length}</code>
"
        f"Default volume: <code>{settings.default_volume}</code>"
    )
