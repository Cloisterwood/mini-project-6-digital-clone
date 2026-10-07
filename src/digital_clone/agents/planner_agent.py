"""Agent 5: orchestrates style, RAG, evaluation, and fallback."""
import json
import time
from pathlib import Path
from typing import Optional

from digital_clone.agents.evaluator_agent import EvaluatorAgent
from digital_clone.agents.fallback_agent import FallbackAgent
from digital_clone.agents.rag_agent import RAGAgent
from digital_clone.agents.style_agent import ChatStyleAgent
from digital_clone.config import CloneConfig
from digital_clone.models import CloneResponse


class PlannerAgent:
    def __init__(self, style_agent: ChatStyleAgent, rag_agent: RAGAgent,
                 evaluator: EvaluatorAgent, fallback: FallbackAgent,
                 config: CloneConfig,
                 decision_log_path: Optional[Path] = None):
        self.style_agent = style_agent
        self.rag_agent = rag_agent
        self.evaluator = evaluator
        self.fallback = fallback
        self.config = config
        self.decision_log_path = decision_log_path

    def process(self, query: str) -> CloneResponse:
        start = time.perf_counter()
        evaluation, citations, styled, error = None, [], None, None
        try:
            retrieved = self.rag_agent.retrieve(query)
            neutral, citations = self.rag_agent.generate(query, retrieved)
            styled = self.style_agent.apply_style(neutral) if neutral else ""
            evaluation = self.evaluator.evaluate(
                query, styled, retrieved, self.style_agent.style_score)
        except Exception as exc:  # any component failure -> graceful fallback
            error = exc

        reason = self.fallback.should_fallback(query, evaluation, error=error)
        latency = time.perf_counter() - start
        if reason is None:
            result = CloneResponse(query=query, delivered=True,
                                   response_text=styled, citations=citations,
                                   evaluation=evaluation, fallback=None,
                                   latency_seconds=latency)
        else:
            fb = self.fallback.build_response(query, evaluation, reason)
            result = CloneResponse(query=query, delivered=False,
                                   response_text=None, citations=[],
                                   evaluation=evaluation, fallback=fb,
                                   latency_seconds=latency)
        self._log(result)
        return result

    def _log(self, result: CloneResponse) -> None:
        if not self.decision_log_path:
            return
        self.decision_log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.decision_log_path, "a") as f:
            f.write(result.model_dump_json() + "\n")


def build_planner(config: CloneConfig, embedder=None) -> PlannerAgent:
    """Load persisted artifacts and wire all five agents (CLI / scripts)."""
    if embedder is None:
        from digital_clone.rag.embedder import SentenceEmbedder
        embedder = SentenceEmbedder()
    style = ChatStyleAgent(config)
    style.load()
    rag = RAGAgent(embedder, config)
    rag.load()
    log_path = config.eval_dir / "decision_log.jsonl"
    return PlannerAgent(style, rag, EvaluatorAgent(config),
                        FallbackAgent(config), config,
                        decision_log_path=log_path)
