from digital_clone.agents.rag_agent import RAGAgent
from digital_clone.config import CloneConfig
from digital_clone.rag.embedder import HashEmbedder


def make_agent(tmp_path, sample_chunks):
    cfg = CloneConfig(data_dir=tmp_path, top_k=3)
    agent = RAGAgent(HashEmbedder(dim=64), cfg)
    agent.build(sample_chunks)
    return agent


def test_build_indexes_all_chunks(tmp_path, sample_chunks):
    agent = make_agent(tmp_path, sample_chunks)
    assert agent.index.size == len(sample_chunks)


def test_retrieve_returns_relevant_chunks(tmp_path, sample_chunks):
    agent = make_agent(tmp_path, sample_chunks)
    results = agent.retrieve("what is the tcp protocol in networking")
    assert len(results) == 3
    assert results[0].chunk.source_topic == "Computer Networking"
    assert all(0.0 <= r.similarity <= 1.0 for r in results)
    assert results[0].similarity >= results[-1].similarity


def test_generate_includes_citations(tmp_path, sample_chunks):
    agent = make_agent(tmp_path, sample_chunks)
    retrieved = agent.retrieve("how do database indexes work")
    answer, citations = agent.generate("how do database indexes work", retrieved)
    assert answer
    assert len(citations) >= 1
    assert citations[0].startswith("[1]")
    assert "Database" in " ".join(citations)


def test_generate_empty_when_no_chunks(tmp_path, sample_chunks):
    agent = make_agent(tmp_path, sample_chunks)
    answer, citations = agent.generate("anything", [])
    assert answer == ""
    assert citations == []


def test_save_load_roundtrip(tmp_path, sample_chunks):
    agent = make_agent(tmp_path, sample_chunks)
    agent.save()
    fresh = RAGAgent(HashEmbedder(dim=64), CloneConfig(data_dir=tmp_path, top_k=3))
    fresh.load()
    assert fresh.index.size == len(sample_chunks)
    assert fresh.retrieve("tcp networking")[0].chunk.source_topic == "Computer Networking"
