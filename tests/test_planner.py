import io
import sys

import pytest

from digital_clone.agents.evaluator_agent import EvaluatorAgent
from digital_clone.agents.fallback_agent import FallbackAgent
from digital_clone.agents.planner_agent import PlannerAgent, build_planner
from digital_clone.agents.rag_agent import RAGAgent
from digital_clone.agents.style_agent import ChatStyleAgent
from digital_clone.cli import main as cli_main
from digital_clone.config import CloneConfig
from digital_clone.rag.embedder import HashEmbedder


@pytest.fixture
def planner(tmp_path, sample_emails, sample_chunks):
    cfg = CloneConfig(data_dir=tmp_path, batch_size=4, pca_components=3, top_k=3)
    style = ChatStyleAgent(cfg)
    style.learn(sample_emails)
    rag = RAGAgent(HashEmbedder(dim=64), cfg)
    rag.build(sample_chunks)
    return PlannerAgent(style, rag, EvaluatorAgent(cfg), FallbackAgent(cfg), cfg,
                        decision_log_path=tmp_path / "decision_log.jsonl")


def test_in_domain_query_returns_response(planner):
    result = planner.process("What is the TCP protocol used for in networking?")
    assert result.latency_seconds < 1.0
    assert result.evaluation is not None
    # delivered or fallback both acceptable; response coherent either way
    if result.delivered:
        assert result.response_text.lower().startswith("hi")
        assert result.citations
    else:
        assert result.fallback is not None


def test_booking_request_always_falls_back(planner):
    result = planner.process("Can we schedule a call to discuss this?")
    assert result.delivered is False
    assert result.fallback.trigger_reason == "user_request"
    assert result.fallback.calendar_link


def test_component_failure_degrades_gracefully(planner):
    planner.rag_agent.index = None  # simulate component failure
    result = planner.process("What is TCP?")
    assert result.delivered is False
    assert result.fallback.trigger_reason == "system_error"


def test_decision_log_written(planner, tmp_path):
    planner.process("What is TCP?")
    planner.process("Can we schedule a call?")
    lines = (tmp_path / "decision_log.jsonl").read_text().strip().splitlines()
    assert len(lines) == 2


# --- Stage 5 additions: factory + CLI rendering on fixture-built artifacts ---


def _saved_artifacts(tmp_path, sample_emails, sample_chunks) -> CloneConfig:
    cfg = CloneConfig(data_dir=tmp_path / "data", batch_size=4,
                      pca_components=3, top_k=3)
    style = ChatStyleAgent(cfg)
    style.learn(sample_emails)
    style.save()
    rag = RAGAgent(HashEmbedder(dim=64), cfg)
    rag.build(sample_chunks)
    rag.save()
    return cfg


def test_build_planner_loads_persisted_artifacts(tmp_path, sample_emails,
                                                 sample_chunks):
    cfg = _saved_artifacts(tmp_path, sample_emails, sample_chunks)
    planner = build_planner(cfg, embedder=HashEmbedder(dim=64))
    assert planner.style_agent.profile is not None
    assert planner.style_agent.profile.n_emails == len(sample_emails)
    assert planner.rag_agent.index.size == len(sample_chunks)
    result = planner.process("Can we schedule a call?")
    assert result.delivered is False
    assert result.fallback.trigger_reason == "user_request"
    assert (cfg.eval_dir / "decision_log.jsonl").exists()


def test_cli_one_shot_renders_deliver_branch(tmp_path, sample_emails,
                                             sample_chunks, monkeypatch, capsys):
    _saved_artifacts(tmp_path, sample_emails, sample_chunks)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("digital_clone.rag.embedder.SentenceEmbedder",
                        lambda: HashEmbedder(dim=64))
    monkeypatch.setattr(sys, "argv",
                        ["cli", "--query", "What is the TCP protocol?"])
    cli_main()
    out = capsys.readouterr().out
    assert "scores:" in out
    assert "-> DELIVER" in out
    assert out.strip().splitlines()[-2].startswith("Hi") or "Hi," in out


def test_cli_one_shot_renders_fallback_branch(tmp_path, sample_emails,
                                              sample_chunks, monkeypatch, capsys):
    _saved_artifacts(tmp_path, sample_emails, sample_chunks)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("digital_clone.rag.embedder.SentenceEmbedder",
                        lambda: HashEmbedder(dim=64))
    monkeypatch.setattr(sys, "argv",
                        ["cli", "--query", "Can we schedule a call?"])
    cli_main()
    out = capsys.readouterr().out
    assert "[FALLBACK: user_request]" in out
    assert "Book here:" in out
    assert "Available slots:" in out
    assert "scores:" in out


def test_cli_repl_processes_query_then_exits_on_eof(tmp_path, sample_emails,
                                                    sample_chunks, monkeypatch,
                                                    capsys):
    _saved_artifacts(tmp_path, sample_emails, sample_chunks)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("digital_clone.rag.embedder.SentenceEmbedder",
                        lambda: HashEmbedder(dim=64))
    monkeypatch.setattr(sys, "argv", ["cli"])
    monkeypatch.setattr(sys, "stdin",
                        io.StringIO("What is the TCP protocol?\n"))
    cli_main()
    out = capsys.readouterr().out
    assert "Ready. 5-agent digital clone online." in out
    assert "-> DELIVER" in out
