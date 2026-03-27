from __future__ import annotations

class LastFMProvider:
    name = "lastfm"

    def __init__(self, api_key: str) -> None:
        self.api_key = api_key
