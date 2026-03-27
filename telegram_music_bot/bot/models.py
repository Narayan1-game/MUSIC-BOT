from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(slots=True)
class Track:
    id: int | None
    source: str
    source_id: str | None
    title: str
    webpage_url: str
    stream_url: str | None
    duration_seconds: int | None
    thumbnail_url: str | None
    uploader: str | None
    requested_by_user_id: int
    requested_by_name: str
    added_at: datetime
    extractor_metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class QueueItem:
    id: int
    chat_id: int
    position: int
    track: Track


@dataclass(slots=True)
class ChatSettings:
    chat_id: int
    admin_only_mode: bool = False
    allow_url_mode: bool = True
    autoplay_enabled: bool = False
    max_queue_length: int = 50
    default_volume: int = 100
    send_thumbnails: bool = True
    edit_status_messages: bool = True
    delete_command_messages: bool = False
    language: str = "en"
    preferred_search_provider: str = "auto"


@dataclass(slots=True)
class PlaybackState:
    chat_id: int
    current_queue_item_id: int | None
    state: str
    repeat_mode: str
    volume: int
    position_seconds: int
    started_at: datetime | None
    updated_at: datetime


@dataclass(slots=True)
class AdminAuditEntry:
    id: int | None
    admin_user_id: int
    action: str
    target: str | None
    details: str | None
    created_at: datetime


@dataclass(slots=True)
class UserActionStats:
    command: str
    chat_id: int
    user_id: int
    used_at: datetime


@dataclass(slots=True)
class BotHealthSnapshot:
    uptime_seconds: int
    total_chats: int
    total_users_seen: int
    total_tracks_queued: int
    total_tracks_played: int
    failed_extraction_count: int
    failed_playback_count: int
    capabilities: dict[str, bool]
