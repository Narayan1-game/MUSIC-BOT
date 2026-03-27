CREATE TABLE IF NOT EXISTS chats (
    chat_id INTEGER PRIMARY KEY,
    title TEXT,
    type TEXT,
    created_at TEXT NOT NULL,
    last_seen_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS chat_settings (
    chat_id INTEGER PRIMARY KEY,
    admin_only_mode INTEGER NOT NULL DEFAULT 0,
    allow_url_mode INTEGER NOT NULL DEFAULT 1,
    autoplay_enabled INTEGER NOT NULL DEFAULT 0,
    max_queue_length INTEGER NOT NULL DEFAULT 50,
    default_volume INTEGER NOT NULL DEFAULT 100,
    send_thumbnails INTEGER NOT NULL DEFAULT 1,
    edit_status_messages INTEGER NOT NULL DEFAULT 1,
    delete_command_messages INTEGER NOT NULL DEFAULT 0,
    language TEXT NOT NULL DEFAULT 'en',
    preferred_search_provider TEXT NOT NULL DEFAULT 'auto',
    FOREIGN KEY(chat_id) REFERENCES chats(chat_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS queue_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id INTEGER NOT NULL,
    position INTEGER NOT NULL,
    source TEXT NOT NULL,
    source_id TEXT,
    title TEXT NOT NULL,
    webpage_url TEXT NOT NULL,
    stream_url TEXT,
    duration_seconds INTEGER,
    thumbnail_url TEXT,
    uploader TEXT,
    requested_by_user_id INTEGER NOT NULL,
    requested_by_name TEXT NOT NULL,
    added_at TEXT NOT NULL,
    extractor_metadata TEXT,
    UNIQUE(chat_id, position)
);

CREATE TABLE IF NOT EXISTS playback_state (
    chat_id INTEGER PRIMARY KEY,
    current_queue_item_id INTEGER,
    state TEXT NOT NULL DEFAULT 'idle',
    repeat_mode TEXT NOT NULL DEFAULT 'off',
    volume INTEGER NOT NULL DEFAULT 100,
    position_seconds INTEGER NOT NULL DEFAULT 0,
    started_at TEXT,
    updated_at TEXT NOT NULL,
    FOREIGN KEY(current_queue_item_id) REFERENCES queue_items(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS banned_users (
    user_id INTEGER PRIMARY KEY,
    reason TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS blacklisted_chats (
    chat_id INTEGER PRIMARY KEY,
    reason TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS track_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id INTEGER NOT NULL,
    source TEXT NOT NULL,
    source_id TEXT,
    title TEXT NOT NULL,
    webpage_url TEXT NOT NULL,
    duration_seconds INTEGER,
    requested_by_user_id INTEGER NOT NULL,
    requested_by_name TEXT NOT NULL,
    played_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS bot_stats (
    key TEXT PRIMARY KEY,
    value INTEGER NOT NULL DEFAULT 0,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS command_usage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    command TEXT NOT NULL,
    chat_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    used_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS admin_audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    admin_user_id INTEGER NOT NULL,
    action TEXT NOT NULL,
    target TEXT,
    details TEXT,
    created_at TEXT NOT NULL
);
