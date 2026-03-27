from __future__ import annotations

import hashlib
import hmac

from bot.constants import CALLBACK_MAX_LEN, CALLBACK_PREFIX


class CallbackDataCodec:
    def __init__(self, secret: str) -> None:
        self.secret = secret.encode("utf-8")

    def encode(self, action: str, chat_id: int, user_id: int, payload: str = "") -> str:
        raw = f"{CALLBACK_PREFIX}|{action}|{chat_id}|{user_id}|{payload}"
        sig = hmac.new(self.secret, raw.encode("utf-8"), hashlib.sha256).hexdigest()[:10]
        data = f"{raw}|{sig}"
        if len(data) > CALLBACK_MAX_LEN:
            raise ValueError("callback payload too long")
        return data

    def decode(self, data: str) -> dict[str, str]:
        if len(data) > CALLBACK_MAX_LEN:
            raise ValueError("Invalid callback size")
        parts = data.split("|")
        if len(parts) != 6 or parts[0] != CALLBACK_PREFIX:
            raise ValueError("Invalid callback format")
        raw = "|".join(parts[:-1])
        expected = hmac.new(self.secret, raw.encode("utf-8"), hashlib.sha256).hexdigest()[:10]
        if not hmac.compare_digest(expected, parts[-1]):
            raise ValueError("Invalid callback signature")
        return {
            "action": parts[1],
            "chat_id": parts[2],
            "user_id": parts[3],
            "payload": parts[4],
        }
