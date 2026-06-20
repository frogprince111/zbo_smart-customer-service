from pathlib import Path

from app.rag.models import Document


class DocumentReader:
    def read_directory(self, path: str | Path) -> list[Document]:
        docs: list[Document] = []
        for file in sorted(Path(path).glob("*.md")):
            docs.append(Document(id=file.stem, text=file.read_text(encoding="utf-8"), source=file.name))
        return docs


class TextCleaner:
    def clean(self, text: str) -> str:
        return "\n".join(line.strip() for line in text.splitlines() if line.strip())


class Chunker:
    def __init__(self, size: int, overlap: int):
        self.size = size
        self.overlap = overlap

    def split(self, docs: list[Document]) -> list:
        from app.rag.models import Chunk

        chunks: list[Chunk] = []
        for doc in docs:
            chunks.append(Chunk(id=f"{doc.id}-0", text=doc.text, source=doc.source))
        return chunks

