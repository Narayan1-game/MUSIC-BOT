from __future__ import annotations

import json
from dataclasses import asdict

import aiosqlite

from bot.constants import HISTORY_RETENTION
from bot.models import AdminAuditEntry, ChatSettings, PlaybackState, QueueItem, Track
from bot.utils.time_utils import utcnow


class Repository:
    def __init__(self, conn: aiosqlite.Connection) -> None:
        self.conn = conn

    async def upsert_chat(self, chat_id: int, title: str | None, chat_type: str) -> None:
        now = utcnow().isoformat()
        await self.conn.execute(
            """
            INSERT INTO chats (chat_id, title, type, created_at, last_seen_at)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(chat_id) DO UPDATE SET title=excluded.title, type=excluded.type, last_seen_at=excluded.last_seen_at
            """,
            (chat_id, title, chat_type, now, now),
        )
        await self.conn.commit()

    async def get_settings(self, chat_id: int, default_volume: int) -> ChatSettings:
        row = await (await self.conn.execute("SELECT * FROM chat_settings WHERE chat_id = ?", (chat_id,))).fetchone()
        if row:
            return ChatSettings(**dict(row))
        settings = ChatSettings(chat_id=chat_id, default_volume=default_volume)
        await self.save_settings(settings)
        return settings

    async def save_settings(self, settings: ChatSettings) -> None:
        await self.conn.execute(
            """
            INSERT INTO chat_settings (
                chat_id, admin_only_mode, allow_url_mode, autoplay_enabled, max_queue_length,
                default_volume, send_thumbnails, edit_status_messages, delete_command_messages,
                language, preferred_search_provider
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(chat_id) DO UPDATE SET
                admin_only_mode=excluded.admin_only_mode,
                allow_url_mode=excluded.allow_url_mode,
                autoplay_enabled=excluded.autoplay_enabled,
                max_queue_length=excluded.max_queue_length,
                default_volume=excluded.default_volume,
                send_thumbnails=excluded.send_thumbnails,
                edit_status_messages=excluded.edit_status_messages,
                delete_command_messages=excluded.delete_command_messages,
                language=excluded.language,
                preferred_search_provider=excluded.preferred_search_provider
            """,
            (
                settings.chat_id,
                int(settings.admin_only_mode),
                int(settings.allow_url_mode),
                int(settings.autoplay_enabled),
                settings.max_queue_length,
                settings.default_volume,
                int(settings.send_thumbnails),
                int(settings.edit_status_messages),
                int(settings.delete_command_messages),
                settings.language,
                settings.preferred_search_provider,
            ),
        )
        await self.conn.commit()

    async def enqueue(self, chat_id: int, track: Track) -> QueueItem:
        row = await (await self.conn.execute("SELECT COALESCE(MAX(position), 0) + 1 AS p FROM queue_items WHERE chat_id=?", (chat_id,))).fetchone()
        pos = int(row["p"])
        cur = await self.conn.execute(
            """
            INSERT INTO queue_items (chat_id, position, source, source_id, title, webpage_url, stream_url,
                                     duration_seconds, thumbnail_url, uploader, requested_by_user_id,
                                     requested_by_name, added_at, extractor_metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                chat_id,
                pos,
                track.source,
                track.source_id,
                track.title,
                track.webpage_url,
                track.stream_url,
                track.duration_seconds,
                track.thumbnail_url,
                track.uploader,
                track.requested_by_user_id,
                track.requested_by_name,
                track.added_at.isoformat(),
                json.dumps(track.extractor_metadata),
            ),
        )
        await self.conn.commit()
        item_id = cur.lastrowid
        return QueueItem(id=item_id, chat_id=chat_id, position=pos, track=track)

    async def queue_items(self, chat_id: int) -> list[QueueItem]:
        rows = await (await self.conn.execute("SELECT * FROM queue_items WHERE chat_id=? ORDER BY position", (chat_id,))).fetchall()
        items: list[QueueItem] = []
        for row in rows:
            d = dict(row)
            track = Track(
                id=d["id"], source=d["source"], source_id=d["source_id"], title=d["title"], webpage_url=d["webpage_url"],
                stream_url=d["stream_url"], duration_seconds=d["duration_seconds"], thumbnail_url=d["thumbnail_url"],
                uploader=d["uploader"], requested_by_user_id=d["requested_by_user_id"], requested_by_name=d["requested_by_name"],
                added_at=utcnow(), extractor_metadata=json.loads(d["extractor_metadata"] or "{}"),
            )
            items.append(QueueItem(id=d["id"], chat_id=d["chat_id"], position=d["position"], track=track))
        return items

    async def pop_next(self, chat_id: int) -> QueueItem | None:
        row = await (await self.conn.execute("SELECT * FROM queue_items WHERE chat_id=? ORDER BY position LIMIT 1", (chat_id,))).fetchone()
        if not row:
            return None
        d = dict(row)
        await self.conn.execute("DELETE FROM queue_items WHERE id=?", (d["id"],))
        await self.conn.execute("UPDATE queue_items SET position = position - 1 WHERE chat_id=?", (chat_id,))
        await self.conn.commit()
        track = Track(
            id=d["id"], source=d["source"], source_id=d["source_id"], title=d["title"], webpage_url=d["webpage_url"],
            stream_url=d["stream_url"], duration_seconds=d["duration_seconds"], thumbnail_url=d["thumbnail_url"], uploader=d["uploader"],
            requested_by_user_id=d["requested_by_user_id"], requested_by_name=d["requested_by_name"], added_at=utcnow(), extractor_metadata={}
        )
        return QueueItem(id=d["id"], chat_id=chat_id, position=1, track=track)

    async def clear_queue(self, chat_id: int) -> None:
        await self.conn.execute("DELETE FROM queue_items WHERE chat_id=?", (chat_id,))
        await self.conn.commit()

    async def set_playback_state(self, state: PlaybackState) -> None:
        await self.conn.execute(
            """INSERT INTO playback_state (chat_id,current_queue_item_id,state,repeat_mode,volume,position_seconds,started_at,updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)
               ON CONFLICT(chat_id) DO UPDATE SET
               current_queue_item_id=excluded.current_queue_item_id,state=excluded.state,repeat_mode=excluded.repeat_mode,
               volume=excluded.volume,position_seconds=excluded.position_seconds,started_at=excluded.started_at,updated_at=excluded.updated_at""",
            (
                state.chat_id,
                state.current_queue_item_id,
                state.state,
                state.repeat_mode,
                state.volume,
                state.position_seconds,
                state.started_at.isoformat() if state.started_at else None,
                state.updated_at.isoformat(),
            ),
        )
        await self.conn.commit()

    async def get_playback_state(self, chat_id: int) -> PlaybackState | None:
        row = await (await self.conn.execute("SELECT * FROM playback_state WHERE chat_id=?", (chat_id,))).fetchone()
        if not row:
            return None
        d = dict(row)
        return PlaybackState(
            chat_id=d["chat_id"], current_queue_item_id=d["current_queue_item_id"], state=d["state"], repeat_mode=d["repeat_mode"],
            volume=d["volume"], position_seconds=d["position_seconds"], started_at=utcnow() if d["started_at"] else None, updated_at=utcnow()
        )

    async def add_history(self, chat_id: int, item: QueueItem) -> None:
        await self.conn.execute(
            """INSERT INTO track_history (chat_id,source,source_id,title,webpage_url,duration_seconds,requested_by_user_id,requested_by_name,played_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                chat_id,
                item.track.source,
                item.track.source_id,
                item.track.title,
                item.track.webpage_url,
                item.track.duration_seconds,
                item.track.requested_by_user_id,
                item.track.requested_by_name,
                utcnow().isoformat(),
            ),
        )
        await self.conn.execute(
            "DELETE FROM track_history WHERE id NOT IN (SELECT id FROM track_history WHERE chat_id=? ORDER BY id DESC LIMIT ?)",
            (chat_id, HISTORY_RETENTION),
        )
        await self.conn.commit()

    async def history(self, chat_id: int, limit: int = 20) -> list[aiosqlite.Row]:
        rows = await (await self.conn.execute("SELECT * FROM track_history WHERE chat_id=? ORDER BY id DESC LIMIT ?", (chat_id, limit))).fetchall()
        return rows

    async def increment_stat(self, key: str, by: int = 1) -> None:
        now = utcnow().isoformat()
        await self.conn.execute(
            "INSERT INTO bot_stats (key, value, updated_at) VALUES (?, ?, ?) ON CONFLICT(key) DO UPDATE SET value=value + excluded.value, updated_at=excluded.updated_at",
            (key, by, now),
        )
        await self.conn.commit()

    async def get_stat(self, key: str) -> int:
        row = await (await self.conn.execute("SELECT value FROM bot_stats WHERE key=?", (key,))).fetchone()
        return int(row["value"]) if row else 0

    async def log_command(self, command: str, chat_id: int, user_id: int) -> None:
        await self.conn.execute(
            "INSERT INTO command_usage (command, chat_id, user_id, used_at) VALUES (?, ?, ?, ?)",
            (command, chat_id, user_id, utcnow().isoformat()),
        )
        await self.conn.commit()

    async def top_commands(self, limit: int = 5) -> list[tuple[str, int]]:
        rows = await (await self.conn.execute("SELECT command, COUNT(*) c FROM command_usage GROUP BY command ORDER BY c DESC LIMIT ?", (limit,))).fetchall()
        return [(r["command"], int(r["c"])) for r in rows]

    async def add_admin_audit(self, entry: AdminAuditEntry) -> None:
        await self.conn.execute(
            "INSERT INTO admin_audit_log (admin_user_id, action, target, details, created_at) VALUES (?, ?, ?, ?, ?)",
            (entry.admin_user_id, entry.action, entry.target, entry.details, entry.created_at.isoformat()),
        )
        await self.conn.commit()

    async def latest_audit(self, limit: int = 20) -> list[aiosqlite.Row]:
        return await (await self.conn.execute("SELECT * FROM admin_audit_log ORDER BY id DESC LIMIT ?", (limit,))).fetchall()

    async def count_chats(self) -> int:
        row = await (await self.conn.execute("SELECT COUNT(*) c FROM chats")).fetchone()
        return int(row["c"])

    async def count_users(self) -> int:
        row = await (await self.conn.execute("SELECT COUNT(DISTINCT user_id) c FROM command_usage")).fetchone()
        return int(row["c"])
