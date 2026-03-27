from __future__ import annotations

import json
from datetime import datetime
from typing import Optional

import aiosqlite

from bot.models import AdminAuditEntry, ChatSettings, PlaybackState, QueueItem, Track
from bot.utils.time_utils import utc_iso_now


class Repository:
    def __init__(self, conn: aiosqlite.Connection) -> None:
        self.conn = conn

    async def upsert_chat(self, chat_id: int, title: str | None, chat_type: str) -> None:
        now = utc_iso_now()
        await self.conn.execute(
            """
            INSERT INTO chats(id,title,type,first_seen_at,last_seen_at) VALUES(?,?,?,?,?)
            ON CONFLICT(id) DO UPDATE SET title=excluded.title,type=excluded.type,last_seen_at=excluded.last_seen_at
            """,
            (chat_id, title, chat_type, now, now),
        )
        await self.conn.commit()

    async def get_settings(self, chat_id: int) -> ChatSettings:
        row = await self.conn.execute_fetchone("SELECT * FROM chat_settings WHERE chat_id=?", (chat_id,))
        if row:
            return ChatSettings(
                chat_id=chat_id,
                admin_only_mode=bool(row["admin_only_mode"]),
                allow_url_mode=bool(row["allow_url_mode"]),
                autoplay_enabled=bool(row["autoplay_enabled"]),
                max_queue_length=row["max_queue_length"],
                default_volume=row["default_volume"],
                send_thumbnails=bool(row["send_thumbnails"]),
                edit_status_messages=bool(row["edit_status_messages"]),
                delete_command_messages=bool(row["delete_command_messages"]),
                language=row["language"],
                preferred_search_provider=row["preferred_search_provider"],
                history_retention=row["history_retention"],
            )
        settings = ChatSettings(chat_id=chat_id)
        await self.save_settings(settings)
        return settings

    async def save_settings(self, settings: ChatSettings) -> None:
        await self.conn.execute(
            """
            INSERT INTO chat_settings(chat_id,admin_only_mode,allow_url_mode,autoplay_enabled,max_queue_length,default_volume,
            send_thumbnails,edit_status_messages,delete_command_messages,language,preferred_search_provider,history_retention,updated_at)
            VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)
            ON CONFLICT(chat_id) DO UPDATE SET
            admin_only_mode=excluded.admin_only_mode,allow_url_mode=excluded.allow_url_mode,autoplay_enabled=excluded.autoplay_enabled,
            max_queue_length=excluded.max_queue_length,default_volume=excluded.default_volume,send_thumbnails=excluded.send_thumbnails,
            edit_status_messages=excluded.edit_status_messages,delete_command_messages=excluded.delete_command_messages,
            language=excluded.language,preferred_search_provider=excluded.preferred_search_provider,history_retention=excluded.history_retention,
            updated_at=excluded.updated_at
            """,
            (
                settings.chat_id, int(settings.admin_only_mode), int(settings.allow_url_mode), int(settings.autoplay_enabled),
                settings.max_queue_length, settings.default_volume, int(settings.send_thumbnails), int(settings.edit_status_messages),
                int(settings.delete_command_messages), settings.language, settings.preferred_search_provider, settings.history_retention,
                utc_iso_now(),
            ),
        )
        await self.conn.commit()

    async def enqueue_track(self, chat_id: int, track: Track) -> QueueItem:
        pos_row = await self.conn.execute_fetchone("SELECT COALESCE(MAX(position), 0) + 1 AS p FROM queue_items WHERE chat_id=?", (chat_id,))
        position = int(pos_row["p"])
        cur = await self.conn.execute(
            """
            INSERT INTO queue_items(chat_id,position,source,source_id,title,webpage_url,stream_url,duration_seconds,thumbnail_url,
            uploader,requested_by_user_id,requested_by_name,added_at,extractor_metadata)
            VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                chat_id, position, track.source, track.source_id, track.title, track.webpage_url, track.stream_url,
                track.duration_seconds, track.thumbnail_url, track.uploader, track.requested_by_user_id, track.requested_by_name,
                track.added_at.isoformat(), json.dumps(track.extractor_metadata),
            ),
        )
        await self.conn.commit()
        return QueueItem(id=cur.lastrowid, chat_id=chat_id, position=position, track=track)

    async def get_queue(self, chat_id: int) -> list[QueueItem]:
        rows = await self.conn.execute_fetchall("SELECT * FROM queue_items WHERE chat_id=? ORDER BY position ASC", (chat_id,))
        data: list[QueueItem] = []
        for r in rows:
            t = Track(
                id=r["id"], source=r["source"], source_id=r["source_id"], title=r["title"], webpage_url=r["webpage_url"],
                stream_url=r["stream_url"], duration_seconds=r["duration_seconds"], thumbnail_url=r["thumbnail_url"], uploader=r["uploader"],
                requested_by_user_id=r["requested_by_user_id"], requested_by_name=r["requested_by_name"],
                added_at=datetime.fromisoformat(r["added_at"]), extractor_metadata=json.loads(r["extractor_metadata"] or "{}"),
            )
            data.append(QueueItem(id=r["id"], chat_id=chat_id, position=r["position"], track=t))
        return data

    async def pop_next(self, chat_id: int) -> Optional[QueueItem]:
        row = await self.conn.execute_fetchone("SELECT * FROM queue_items WHERE chat_id=? ORDER BY position ASC LIMIT 1", (chat_id,))
        if not row:
            return None
        await self.conn.execute("DELETE FROM queue_items WHERE id=?", (row["id"],))
        await self.conn.execute("UPDATE queue_items SET position = position - 1 WHERE chat_id=? AND position > ?", (chat_id, row["position"]))
        await self.conn.commit()
        track = Track(
            id=row["id"], source=row["source"], source_id=row["source_id"], title=row["title"], webpage_url=row["webpage_url"],
            stream_url=row["stream_url"], duration_seconds=row["duration_seconds"], thumbnail_url=row["thumbnail_url"], uploader=row["uploader"],
            requested_by_user_id=row["requested_by_user_id"], requested_by_name=row["requested_by_name"],
            added_at=datetime.fromisoformat(row["added_at"]), extractor_metadata=json.loads(row["extractor_metadata"] or "{}"),
        )
        return QueueItem(id=row["id"], chat_id=chat_id, position=1, track=track)

    async def remove_index(self, chat_id: int, index: int) -> bool:
        row = await self.conn.execute_fetchone("SELECT id,position FROM queue_items WHERE chat_id=? AND position=?", (chat_id, index))
        if not row:
            return False
        await self.conn.execute("DELETE FROM queue_items WHERE id=?", (row["id"],))
        await self.conn.execute("UPDATE queue_items SET position = position - 1 WHERE chat_id=? AND position > ?", (chat_id, index))
        await self.conn.commit()
        return True

    async def clear_queue(self, chat_id: int) -> int:
        cur = await self.conn.execute("DELETE FROM queue_items WHERE chat_id=?", (chat_id,))
        await self.conn.commit()
        return cur.rowcount

    async def save_playback_state(self, state: PlaybackState) -> None:
        await self.conn.execute(
            """
            INSERT INTO playback_state(chat_id,current_queue_item_id,status,repeat_mode,volume,started_at,elapsed_seconds,updated_at)
            VALUES(?,?,?,?,?,?,?,?)
            ON CONFLICT(chat_id) DO UPDATE SET current_queue_item_id=excluded.current_queue_item_id,status=excluded.status,
            repeat_mode=excluded.repeat_mode,volume=excluded.volume,started_at=excluded.started_at,elapsed_seconds=excluded.elapsed_seconds,
            updated_at=excluded.updated_at
            """,
            (
                state.chat_id, state.current_queue_item_id, state.status, state.repeat_mode, state.volume,
                state.started_at.isoformat() if state.started_at else None, state.elapsed_seconds, utc_iso_now(),
            ),
        )
        await self.conn.commit()

    async def get_playback_state(self, chat_id: int) -> PlaybackState:
        row = await self.conn.execute_fetchone("SELECT * FROM playback_state WHERE chat_id=?", (chat_id,))
        if row:
            started_at = datetime.fromisoformat(row["started_at"]) if row["started_at"] else None
            return PlaybackState(
                chat_id=chat_id,
                current_queue_item_id=row["current_queue_item_id"],
                status=row["status"],
                repeat_mode=row["repeat_mode"],
                volume=row["volume"],
                started_at=started_at,
                elapsed_seconds=row["elapsed_seconds"],
            )
        state = PlaybackState(chat_id=chat_id, current_queue_item_id=None, status="stopped", repeat_mode="off", volume=100, started_at=None, elapsed_seconds=0)
        await self.save_playback_state(state)
        return state

    async def add_history(self, chat_id: int, track: Track) -> None:
        await self.conn.execute(
            """
            INSERT INTO track_history(chat_id,source,source_id,title,webpage_url,duration_seconds,requested_by_user_id,requested_by_name,played_at)
            VALUES(?,?,?,?,?,?,?,?,?)
            """,
            (chat_id, track.source, track.source_id, track.title, track.webpage_url, track.duration_seconds, track.requested_by_user_id, track.requested_by_name, utc_iso_now()),
        )
        await self.conn.commit()

    async def get_history(self, chat_id: int, limit: int = 10) -> list[dict]:
        rows = await self.conn.execute_fetchall("SELECT * FROM track_history WHERE chat_id=? ORDER BY id DESC LIMIT ?", (chat_id, limit))
        return [dict(r) for r in rows]

    async def record_command(self, command: str, chat_id: int | None, user_id: int | None) -> None:
        await self.conn.execute("INSERT INTO command_usage(command,chat_id,user_id,used_at) VALUES(?,?,?,?)", (command, chat_id, user_id, utc_iso_now()))
        await self.conn.commit()

    async def command_top(self, limit: int = 10) -> list[tuple[str, int]]:
        rows = await self.conn.execute_fetchall("SELECT command,COUNT(*) c FROM command_usage GROUP BY command ORDER BY c DESC LIMIT ?", (limit,))
        return [(r["command"], r["c"]) for r in rows]

    async def add_audit_entry(self, entry: AdminAuditEntry) -> None:
        await self.conn.execute(
            "INSERT INTO admin_audit_log(admin_user_id,action,target_type,target_id,details,created_at) VALUES(?,?,?,?,?,?)",
            (entry.admin_user_id, entry.action, entry.target_type, entry.target_id, entry.details, entry.created_at.isoformat()),
        )
        await self.conn.commit()

    async def get_audit_entries(self, limit: int = 20) -> list[dict]:
        rows = await self.conn.execute_fetchall("SELECT * FROM admin_audit_log ORDER BY id DESC LIMIT ?", (limit,))
        return [dict(r) for r in rows]
