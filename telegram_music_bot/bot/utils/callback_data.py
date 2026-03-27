from __future__ import annotations

import base64
import hashlib
import hmac

from bot.constants import MAX_CALLBACK_PAYLOAD


class CallbackSigner:
    def __init__(self, secret: str) -> None:
        self.secret = secret.encode("utf-8")

    def sign(self, payload: str) -> str:
        digest = hmac.new(self.secret, payload.encode("utf-8"), hashlib.sha256).digest()[:8]
        token = f"{payload}:{base64.urlsafe_b64encode(digest).decode('ascii')}"
        if len(token) > MAX_CALLBACK_PAYLOAD:
            raise ValueError("callback payload too long")
        return token

    def verify(self, token: str) -> str:
        payload, sig = token.rsplit(":", 1)
        expected = self.sign(payload).rsplit(":", 1)[1]
        if not hmac.compare_digest(sig, expected):
            raise ValueError("Invalid callback signature")
        return payload
