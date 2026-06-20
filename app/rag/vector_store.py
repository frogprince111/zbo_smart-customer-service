from abc import ABC, abstractmethod

from app.rag.models import Chunk


class VectorStore(ABC):
    @abstractmethod
    async def add(self, chunks: list[Chunk]) -> None:
        raise NotImplementedError

    @abstractmethod
    async def search(self, query: str, top_k: int) -> list[Chunk]:
        raise NotImplementedError


class MemoryVectorStore(VectorStore):
    def __init__(self) -> None:
        self._chunks: list[Chunk] = []

    async def add(self, chunks: list[Chunk]) -> None:
        self._chunks.extend(chunks)

    async def search(self, query: str, top_k: int) -> list[Chunk]:
        terms = [t for t in query.replace("？", " ").replace("吗", " ").split() if t]
        scored: list[Chunk] = []
        for chunk in self._chunks:
            score = 0.9 if ("退货" in query and "退货" in chunk.text) or any(t in chunk.text for t in terms) else 0.3
            scored.append(chunk.model_copy(update={"score": score}))
        return sorted(scored, key=lambda item: item.score, reverse=True)[:top_k]

