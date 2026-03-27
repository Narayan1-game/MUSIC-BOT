from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional


def utcnow() -> datetime:
    return datetime.now(tz=timezone.utc)


@dataclass(slots=True)
class Track:
    id: Optional[int]
    source: str
    source_id: str
    title: str
    webpage_url: Optional[str]
    stream_url: Optional[str]
    duration_seconds: Optional[int]
    thumbnail_url: Optional[str]
    uploader: Optional[str]
    requested_by_user_id: int
    requested_by_name: str
    added_at: datetime = field(default_factory=utcnow)
    extractor_metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class QueueItem:
    id: Optional[int]
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
    history_retention: int = 200


@dataclass(slots=True)
class PlaybackState:
    chat_id: int
    current_queue_item_id: Optional[int]
    status: str
    repeat_mode: str
    volume: int
    started_at: Optional[datetime]
    elapsed_seconds: int


@dataclass(slots=True)
class AdminAuditEntry:
    admin_user_id: int
    action: str
    target_type: Optional[str]
    target_id: Optional[str]
    details: Optional[str]
    created_at: datetime = field(default_factory=utcnow)


@dataclass(slots=True)
class UserActionStats:
    command: str
    chat_id: int
    user_id: int
    used_at: datetime = field(default_factory=utcnow)


@dataclass(slots=True)
class BotHealthSnapshot:
    uptime_seconds: int
    total_chats: int
    total_users: int
    total_tracks_queued: int
    total_tracks_played: int
    failed_extractions: int
    failed_playback: int
    capabilities: dict[str, bool]
