"""Embedding backends. HashEmbedder keeps unit tests offline and fast;
SentenceEmbedder is used by the real pipeline scripts."""
import hashlib
import re

import numpy as np


class HashEmbedder:
    def __init__(self, dim: int = 64):
        self.dim = dim

    def encode(self, texts: list[str]) -> np.ndarray:
        out = np.zeros((len(texts), self.dim), dtype=np.float32)
        for i, text in enumerate(texts):
            for word in re.findall(r"[a-z']+", text.lower()):
                h = int(hashlib.md5(word.encode()).hexdigest(), 16)
                out[i, h % self.dim] += 1.0
        return out


class SentenceEmbedder:
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        from sentence_transformers import SentenceTransformer  # lazy heavy import
        self.model = SentenceTransformer(model_name)
        self.dim = self.model.get_sentence_embedding_dimension()

    def encode(self, texts: list[str]) -> np.ndarray:
        return np.asarray(self.model.encode(texts, show_progress_bar=False),
                          dtype=np.float32)
