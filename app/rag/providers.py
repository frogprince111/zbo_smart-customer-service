from abc import ABC, abstractmethod


class EmbeddingProvider(ABC):
    @abstractmethod
    async def health_check(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def embed(self, text: str) -> list[float]:
        raise NotImplementedError


class MockEmbeddingProvider(EmbeddingProvider):
    def __init__(self, dimension: int = 1024):
        self.dimension = dimension

    async def health_check(self) -> bool:
        return True

    async def embed(self, text: str) -> list[float]:
        return [float((sum(map(ord, text)) + idx) % 17) / 17 for idx in range(self.dimension)]


class RerankProvider(ABC):
    @abstractmethod
    async def health_check(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def rerank(self, query: str, texts: list[str]) -> list[float]:
        raise NotImplementedError


class MockRerankProvider(RerankProvider):
    async def health_check(self) -> bool:
        return True

    async def rerank(self, query: str, texts: list[str]) -> list[float]:
        return [1.0 if any(term in text for term in query.split()) else 0.5 for text in texts]

