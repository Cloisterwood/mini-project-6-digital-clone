import pytest

from digital_clone.agents.evaluator_agent import EvaluatorAgent
from digital_clone.config import CloneConfig
from digital_clone.models import KnowledgeChunk, RetrievedChunk


def make_retrieved(sim=0.8, content="TCP is a connection-oriented transport protocol."):
    chunk = KnowledgeChunk(content=content, source_topic="Networking",
                           source_field="CS", chunk_index=0)
    return [RetrievedChunk(chunk=chunk, similarity=sim)]


def test_final_score_is_weighted_sum():
    agent = EvaluatorAgent(CloneConfig())
    result = agent.evaluate(
        query="what is tcp",
        response="TCP is a connection-oriented transport protocol." * 3,
        retrieved=make_retrieved(sim=0.9),
        style_scorer=lambda text: 0.95,
    )
    expected = (0.4 * result.style_score + 0.4 * result.groundedness_score
                + 0.2 * result.confidence_score)
    assert abs(result.final_score - expected) < 1e-9


def test_decision_threshold():
    agent = EvaluatorAgent(CloneConfig())
    high = agent.evaluate("q", "TCP is a connection-oriented transport protocol." * 4,
                          make_retrieved(sim=0.95), lambda t: 0.95)
    low = agent.evaluate("q", "hmm", make_retrieved(sim=0.05, content="unrelated"),
                         lambda t: 0.1)
    assert high.decision == "deliver"
    assert low.decision == "fallback"


def test_hedging_reduces_confidence():
    agent = EvaluatorAgent(CloneConfig())
    plain = "TCP is a connection-oriented transport protocol." * 3
    hedged = plain + " I'm not sure, it might be different, possibly."
    conf_plain, hedges_plain = agent.confidence(plain, make_retrieved())
    conf_hedged, hedges_hedged = agent.confidence(hedged, make_retrieved())
    assert hedges_plain == 0
    assert hedges_hedged >= 3
    assert conf_hedged < conf_plain


def test_groundedness_rewards_overlap():
    agent = EvaluatorAgent(CloneConfig())
    grounded = agent.groundedness(
        "TCP is a connection-oriented transport protocol.", make_retrieved())
    ungrounded = agent.groundedness(
        "Bananas are yellow fruit grown in tropical climates.", make_retrieved())
    assert grounded > ungrounded


def test_empty_retrieval_scores_zero_groundedness():
    agent = EvaluatorAgent(CloneConfig())
    result = agent.evaluate("q", "some response text here", [], lambda t: 0.9)
    assert result.groundedness_score == 0.0
    assert result.decision == "fallback"


# --- Stage 4 additions: threshold boundaries (prep for S7 tuning) -----------

def eval_at_final_score(agent, target, response, retrieved):
    """Evaluate with a mock style score solved so final lands on `target`."""
    grounded = agent.groundedness(response, retrieved)
    conf, _ = agent.confidence(response, retrieved)
    style = (target - agent.config.groundedness_weight * grounded
             - agent.config.confidence_weight * conf) / agent.config.style_weight
    return agent.evaluate("q", response, retrieved, lambda text: style)


@pytest.mark.parametrize("threshold", [0.70, 0.75, 0.80])
def test_decision_boundary_tracks_config_threshold(threshold):
    agent = EvaluatorAgent(CloneConfig(fallback_threshold=threshold))
    response = "TCP is a connection-oriented transport protocol." * 3
    retrieved = make_retrieved()
    below = eval_at_final_score(agent, threshold - 0.01, response, retrieved)
    above = eval_at_final_score(agent, threshold + 0.01, response, retrieved)
    assert below.final_score < threshold
    assert below.decision == "fallback"
    assert above.final_score > threshold
    assert above.decision == "deliver"


@pytest.mark.parametrize("threshold", [0.70, 0.75, 0.80])
def test_deliver_iff_final_at_or_above_threshold(threshold):
    agent = EvaluatorAgent(CloneConfig(fallback_threshold=threshold))
    response = "TCP is a connection-oriented transport protocol." * 3
    retrieved = make_retrieved()
    at = eval_at_final_score(agent, threshold, response, retrieved)
    # The computed final sits on the boundary up to float error; the rule
    # under test is exactly "deliver iff final >= threshold".
    expected = "deliver" if at.final_score >= threshold else "fallback"
    assert at.decision == expected
    assert abs(at.final_score - threshold) < 1e-9


def test_confidence_clipped_to_unit_range():
    agent = EvaluatorAgent(CloneConfig())
    filler = ("possibly i think maybe perhaps " * 30).strip()
    conf, hedges = agent.confidence(filler, make_retrieved(sim=0.0))
    assert hedges > 3
    assert conf == 0.0  # 0.3*completeness - 0.5 penalty < 0 -> clipped
