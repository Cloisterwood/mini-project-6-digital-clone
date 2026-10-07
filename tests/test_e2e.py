"""End-to-end: 5 query types through the full pipeline, no crashes."""
import pytest

from digital_clone.agents.evaluator_agent import EvaluatorAgent
from digital_clone.agents.fallback_agent import FallbackAgent
from digital_clone.agents.planner_agent import PlannerAgent
from digital_clone.agents.rag_agent import RAGAgent
from digital_clone.agents.style_agent import ChatStyleAgent
from digital_clone.config import CloneConfig
from digital_clone.rag.embedder import HashEmbedder

QUERIES = [
    ("in_domain_factual", "What is the TCP protocol?"),
    ("in_domain_howto", "How does a database index speed up queries?"),
    ("out_of_domain", "What's the weather like in Houston today?"),
    ("ambiguous", "Tell me about it"),
    ("booking_request", "I'd like to schedule a call with you"),
]


@pytest.fixture
def planner(tmp_path, sample_emails, sample_chunks):
    cfg = CloneConfig(data_dir=tmp_path, batch_size=4, pca_components=3, top_k=3)
    style = ChatStyleAgent(cfg)
    style.learn(sample_emails)
    rag = RAGAgent(HashEmbedder(dim=64), cfg)
    rag.build(sample_chunks)
    return PlannerAgent(style, rag, EvaluatorAgent(cfg), FallbackAgent(cfg), cfg)


def test_all_query_types_complete(planner):
    for qtype, query in QUERIES:
        result = planner.process(query)
        assert result.latency_seconds < 1.0, f"{qtype} too slow"
        assert result.delivered or result.fallback is not None, f"{qtype} no output"


def test_booking_and_out_of_domain_fall_back(planner):
    booking = planner.process("I'd like to schedule a call with you")
    assert booking.fallback.trigger_reason == "user_request"
