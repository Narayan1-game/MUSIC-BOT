from __future__ import annotations

import ipaddress
from urllib.parse import urlparse

from bot.constants import MAX_QUERY_LENGTH


def validate_query(query: str) -> str:
    q = query.strip()
    if not q:
        raise ValueError("Query is required")
    if len(q) > MAX_QUERY_LENGTH:
        raise ValueError("Query is too long")
    return q


def is_valid_url(url: str) -> bool:
    parsed = urlparse(url.strip())
    if parsed.scheme not in {"http", "https"}:
        return False
    host = parsed.hostname
    if not host:
        return False
    try:
        ip = ipaddress.ip_address(host)
        if ip.is_private or ip.is_loopback or ip.is_link_local:
            return False
    except ValueError:
        blocked = {"localhost", "127.0.0.1", "::1"}
        if host.lower() in blocked:
            return False
    return True
