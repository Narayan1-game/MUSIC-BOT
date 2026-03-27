from __future__ import annotations

from abc import ABC, abstractmethod

from bot.models import Track


class ProviderError(Exception):
    pass


class BaseProvider(ABC):
    name: str

    @abstractmethod
    async def search(self, query: str, requester_id: int, requester_name: str) -> list[Track]:
        raise NotImplementedError

    @abstractmethod
    async def extract(self, url_or_query: str, requester_id: int, requester_name: str) -> Track:
        raise NotImplementedError
