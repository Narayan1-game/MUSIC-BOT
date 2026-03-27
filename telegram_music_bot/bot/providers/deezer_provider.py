from __future__ import annotations

class DeezerProvider:
    name = "deezer"

    def __init__(self, app_id: str, app_secret: str) -> None:
        self.app_id = app_id
        self.app_secret = app_secret
