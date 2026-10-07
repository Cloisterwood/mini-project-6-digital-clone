"""Agent 2: knowledge retrieval with citations."""
import json
import re
from typing import Optional

import numpy as np

from digital_clone.config import CloneConfig
from digital_clone.models import KnowledgeChunk, RetrievedChunk
from digital_clone.rag.index import VectorIndex


class RAGAgent:
    def __init__(self, embedder, config: CloneConfig):
        self.embedder = embedder
        self.config = config
        self.chunks: list[KnowledgeChunk] = []
        self.index: Optional[VectorIndex] = None

    def build(self, chunks: list[KnowledgeChunk]) -> int:
        self.chunks = chunks
        self.index = VectorIndex(dim=self.embedder.dim)
        embeddings = self.embedder.encode([c.content for c in chunks])
        self.index.add(embeddings)
        return self.index.size

    def retrieve(self, query: str, k: Optional[int] = None) -> list[RetrievedChunk]:
        k = k or self.config.top_k
        query_vec = self.embedder.encode([query])[0]
        scores, ids = self.index.search(query_vec, min(k, self.index.size))
        return [
            RetrievedChunk(chunk=self.chunks[idx],
                           similarity=float(np.clip(score, 0.0, 1.0)))
            for score, idx in zip(scores, ids) if idx >= 0
        ]

    def generate(self, query: str, retrieved: list[RetrievedChunk]) -> tuple[str, list[str]]:
        if not retrieved:
            return "", []
        parts, citations = [], []
        for i, r in enumerate(retrieved[:3]):
            sentences = re.split(r"(?<=[.!?])\s+", r.chunk.content.strip())
            parts.append(" ".join(sentences[:2]))
            citations.append(f"[{i + 1}] {r.chunk.source_topic} (chunk {r.chunk.chunk_index})")
        answer = ("Here's what I can tell you: " + " ".join(parts)
                  + " (Sources: " + "; ".join(citations) + ")")
        return answer, citations

    def save(self) -> None:
        index_path = self.config.rag_dir / "faiss_index" / "index.faiss"
        self.index.save(index_path)
        meta_path = self.config.rag_dir / "chunks_metadata.json"
        meta_path.parent.mkdir(parents=True, exist_ok=True)
        meta_path.write_text(json.dumps([c.model_dump() for c in self.chunks]))

    def load(self) -> int:
        index_path = self.config.rag_dir / "faiss_index" / "index.faiss"
        self.index = VectorIndex.load(index_path)
        meta_path = self.config.rag_dir / "chunks_metadata.json"
        self.chunks = [KnowledgeChunk.model_validate(c)
                       for c in json.loads(meta_path.read_text())]
        return self.index.size
