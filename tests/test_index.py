import numpy as np

from digital_clone.rag.embedder import HashEmbedder
from digital_clone.rag.index import VectorIndex


def test_hash_embedder_deterministic():
    emb = HashEmbedder(dim=32)
    a = emb.encode(["the tcp protocol", "database indexing"])
    b = emb.encode(["the tcp protocol", "database indexing"])
    assert a.shape == (2, 32)
    assert a.dtype == np.float32
    np.testing.assert_array_equal(a, b)


def test_similar_texts_score_higher():
    emb = HashEmbedder(dim=64)
    vecs = emb.encode([
        "tcp is a transport protocol for networking",
        "sql databases store relational tables",
    ])
    index = VectorIndex(dim=64)
    index.add(vecs)
    q = emb.encode(["what is the tcp networking protocol"])[0]
    scores, ids = index.search(q, k=2)
    assert ids[0] == 0            # networking chunk ranks first
    assert scores[0] > scores[1]


def test_index_search_is_normalized():
    emb = HashEmbedder(dim=64)
    index = VectorIndex(dim=64)
    index.add(emb.encode(["alpha beta gamma"]))
    q = emb.encode(["alpha beta gamma"])[0]
    scores, _ = index.search(q, k=1)
    assert abs(scores[0] - 1.0) < 1e-5   # identical text = cosine 1.0


def test_save_load_roundtrip(tmp_path):
    emb = HashEmbedder(dim=64)
    index = VectorIndex(dim=64)
    index.add(emb.encode(["one", "two", "three"]))
    p = tmp_path / "index.faiss"
    index.save(p)
    loaded = VectorIndex.load(p)
    assert loaded.size == 3
