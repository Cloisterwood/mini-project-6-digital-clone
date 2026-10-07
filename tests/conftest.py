import json
from pathlib import Path

import pytest

from digital_clone.models import EmailMessage, KnowledgeChunk

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def sample_emails() -> list[EmailMessage]:
    raw = json.loads((FIXTURES / "sample_emails.json").read_text())
    return [EmailMessage.model_validate(e) for e in raw]


@pytest.fixture
def sample_chunks() -> list[KnowledgeChunk]:
    raw = json.loads((FIXTURES / "sample_corpus.json").read_text())
    chunks = []
    for doc in raw:
        for i, para in enumerate(doc["markdown"].split("\n\n")):
            if para.strip():
                chunks.append(KnowledgeChunk(
                    content=para.strip(), source_topic=doc["topic"],
                    source_field=doc["field"], chunk_index=len(chunks)))
    return chunks
