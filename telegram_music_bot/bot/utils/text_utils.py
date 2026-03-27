from __future__ import annotations

from html import escape


def safe_html(text: str) -> str:
    return escape(text or "")
