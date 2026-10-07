"""Agent 3: multi-metric quality evaluation.
FinalScore = w_style * style + w_grounded * groundedness + w_conf * confidence."""
import re
from typing import Callable

import numpy as np

from digital_clone.config import CloneConfig
from digital_clone.models import EvaluationResult, RetrievedChunk

HEDGING_PHRASES = ["i'm not sure", "im not sure", "might be", "possibly",
                   "i think", "perhaps", "not certain", "maybe"]


def _tokens(text: str) -> set[str]:
    return set(re.findall(r"[a-z']+", text.lower()))


class EvaluatorAgent:
    def __init__(self, config: CloneConfig):
        self.config = config

    def groundedness(self, response: str, retrieved: list[RetrievedChunk]) -> float:
        if not retrieved or not response:
            return 0.0
        mean_sim = float(np.mean([r.similarity for r in retrieved]))
        chunk_tokens: set[str] = set()
        for r in retrieved:
            chunk_tokens |= _tokens(r.chunk.content)
        resp_tokens = _tokens(response)
        overlap = len(resp_tokens & chunk_tokens) / max(len(resp_tokens), 1)
        return float(np.clip(0.5 * mean_sim + 0.5 * overlap, 0.0, 1.0))

    def confidence(self, response: str, retrieved: list[RetrievedChunk]) -> tuple[float, int]:
        relevance = float(np.mean([r.similarity for r in retrieved])) if retrieved else 0.0
        completeness = float(np.clip(
            len(response) / self.config.expected_response_length, 0.0, 1.0))
        lowered = response.lower()
        hedge_count = sum(lowered.count(p) for p in HEDGING_PHRASES)
        penalty = float(np.clip(hedge_count * 0.15, 0.0, 0.5))
        score = float(np.clip(
            self.config.confidence_relevance_weight * relevance
            + self.config.confidence_completeness_weight * completeness - penalty,
            0.0, 1.0))
        return score, hedge_count

    def evaluate(self, query: str, response: str,
                 retrieved: list[RetrievedChunk],
                 style_scorer: Callable[[str], float]) -> EvaluationResult:
        style = float(np.clip(style_scorer(response), 0.0, 1.0))
        grounded = self.groundedness(response, retrieved)
        conf, hedge_count = self.confidence(response, retrieved)
        final = (self.config.style_weight * style
                 + self.config.groundedness_weight * grounded
                 + self.config.confidence_weight * conf)
        decision = "deliver" if final >= self.config.fallback_threshold else "fallback"
        return EvaluationResult(
            style_score=style, groundedness_score=grounded,
            confidence_score=conf, final_score=float(np.clip(final, 0.0, 1.0)),
            hedge_count=hedge_count, decision=decision)
