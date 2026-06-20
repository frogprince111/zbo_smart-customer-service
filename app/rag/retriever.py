from app.rag.models import Chunk
from app.rag.providers import RerankProvider
from app.rag.vector_store import VectorStore


class Retriever:
    def __init__(self, vector_store: VectorStore, reranker: RerankProvider, top_k: int, top_n: int, threshold: float):
        self.vector_store = vector_store
        self.reranker = reranker
        self.top_k = top_k
        self.top_n = top_n
        self.threshold = threshold

    async def retrieve(self, query: str) -> list[Chunk]:
        chunks = await self.vector_store.search(query, self.top_k)
        chunks = [chunk for chunk in chunks if chunk.score >= self.threshold]
        scores = await self.reranker.rerank(query, [chunk.text for chunk in chunks])
        reranked = [
            chunk.model_copy(update={"score": max(chunk.score, score)})
            for chunk, score in zip(chunks, scores, strict=False)
        ]
        return sorted(reranked, key=lambda item: item.score, reverse=True)[: self.top_n]

