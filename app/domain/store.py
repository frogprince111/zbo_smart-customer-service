from abc import ABC, abstractmethod

from app.domain.models import Tracker


class TrackerStore(ABC):
    @abstractmethod
    async def get_or_create(self, sender_id: str) -> Tracker:
        raise NotImplementedError

    @abstractmethod
    async def save(self, tracker: Tracker) -> None:
        raise NotImplementedError


class MemoryTrackerStore(TrackerStore):
    def __init__(self) -> None:
        self._items: dict[str, Tracker] = {}

    async def get_or_create(self, sender_id: str) -> Tracker:
        if sender_id not in self._items:
            self._items[sender_id] = Tracker(sender_id=sender_id)
        return self._items[sender_id]

    async def save(self, tracker: Tracker) -> None:
        self._items[tracker.sender_id] = tracker

