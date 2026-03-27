from __future__ import annotations

class YouTubeApiProvider:
    name = "youtube_api"

    def __init__(self, api_key: str) -> None:
        self.api_key = api_key
