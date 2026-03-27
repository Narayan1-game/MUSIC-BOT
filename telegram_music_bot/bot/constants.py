from __future__ import annotations

from enum import Enum


class RepeatMode(str, Enum):
    OFF = "off"
    ONE = "one"
    ALL = "all"


CALLBACK_PREFIX = "mb"
CALLBACK_MAX_LEN = 64
QUERY_MAX_LEN = 200
SEARCH_LIMIT = 5
QUEUE_PAGE_SIZE = 10
COOLDOWN_SECONDS = {
    "play": 3,
    "search": 3,
    "lyrics": 5,
    "callback": 1,
}
