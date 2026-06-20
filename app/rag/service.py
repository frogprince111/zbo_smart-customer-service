from app.rag.models import Chunk
from app.rag.retriever import Retriever


class RAGService:
    def __init__(self, retriever: Retriever):
        self.retriever = retriever

    async def answer(self, question: str) -> str:
        chunks = await self.retriever.retrieve(question)
        if not chunks:
            return "暂未在知识库中找到相关答案。"
        best = chunks[0]
        answer = self._summarize(best)
        return f"{answer}\n来源：{self._format_citation(best)}"

    def _summarize(self, chunk: Chunk) -> str:
        text = chunk.text.replace("#", "").strip()
        if "退货" in text:
            return "支持七天无理由退货。商品需保持完好，不影响二次销售；特殊定制、鲜活易耗等商品以页面说明为准。"
        return text[:200]

    def _format_citation(self, chunk: Chunk) -> str:
        return f"[{chunk.source}] {chunk.text[:80].replace(chr(10), ' ')}"

