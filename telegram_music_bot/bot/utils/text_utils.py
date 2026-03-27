from __future__ import annotations


def truncate(text: str, max_len: int = 180) -> str:
    if len(text) <= max_len:
        return text
    return text[: max_len - 1] + "…"
