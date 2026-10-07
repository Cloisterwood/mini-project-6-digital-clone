"""FAISS IndexFlatIP over L2-normalized vectors = exact cosine similarity."""
from pathlib import Path

import faiss
import numpy as np


class VectorIndex:
    def __init__(self, dim: int):
        self.index = faiss.IndexFlatIP(dim)

    @property
    def size(self) -> int:
        return self.index.ntotal

    def add(self, embeddings: np.ndarray) -> None:
        vecs = np.ascontiguousarray(embeddings, dtype=np.float32)
        faiss.normalize_L2(vecs)
        self.index.add(vecs)

    def search(self, query_vec: np.ndarray, k: int):
        q = np.ascontiguousarray(query_vec.reshape(1, -1), dtype=np.float32)
        faiss.normalize_L2(q)
        scores, ids = self.index.search(q, k)
        return scores[0], ids[0]

    def save(self, path: Path) -> None:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        faiss.write_index(self.index, str(path))

    @classmethod
    def load(cls, path: Path) -> "VectorIndex":
        obj = cls.__new__(cls)
        obj.index = faiss.read_index(str(path))
        return obj
