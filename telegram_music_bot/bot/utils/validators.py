from __future__ import annotations

from urllib.parse import urlparse
import ipaddress

from bot.constants import QUERY_MAX_LEN


class ValidationError(ValueError):
    pass


def validate_query(query: str) -> str:
    q = query.strip()
    if not q:
        raise ValidationError("Query is required")
    if len(q) > QUERY_MAX_LEN:
        raise ValidationError(f"Query too long (max {QUERY_MAX_LEN})")
    return q


def validate_url(url: str) -> str:
    parsed = urlparse(url.strip())
    if parsed.scheme not in {"http", "https"}:
        raise ValidationError("Only http/https URLs are supported")
    host = (parsed.hostname or "").lower()
    if not host:
        raise ValidationError("Invalid URL host")
    if host in {"localhost"}:
        raise ValidationError("localhost URLs are not allowed")
    try:
        ip = ipaddress.ip_address(host)
        if ip.is_private or ip.is_loopback or ip.is_link_local:
            raise ValidationError("Private network URLs are not allowed")
    except ValueError:
        pass
    return url.strip()


def is_url(value: str) -> bool:
    parsed = urlparse(value.strip())
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)
