import json
from pathlib import Path

from digital_clone.rag.chunker import chunk_documents

FIXTURE = Path(__file__).parent / "fixtures" / "sample_corpus.json"


def docs():
    return json.loads(FIXTURE.read_text())


def test_chunks_respect_size():
    chunks = chunk_documents(docs(), chunk_size=200, chunk_overlap=20)
    assert all(len(c.content) <= 200 for c in chunks)
    assert len(chunks) > 10


def test_chunk_metadata_preserved():
    chunks = chunk_documents(docs(), chunk_size=200, chunk_overlap=20)
    topics = {c.source_topic for c in chunks}
    assert "Computer Networking" in topics
    assert all(c.source_field for c in chunks)


def test_chunk_indices_sequential():
    chunks = chunk_documents(docs(), chunk_size=200, chunk_overlap=20)
    assert [c.chunk_index for c in chunks] == list(range(len(chunks)))


def test_empty_doc_skipped():
    chunks = chunk_documents([{"markdown": "", "topic": "t", "field": "f"}])
    assert chunks == []
