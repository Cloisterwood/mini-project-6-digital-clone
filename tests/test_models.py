from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from digital_clone.models import (
    CloneResponse,
    EmailMessage,
    EvaluationResult,
    FallbackResponse,
    KnowledgeChunk,
    RetrievedChunk,
    StyleProfile,
)


def test_email_message_roundtrip():
    msg = EmailMessage(
        sender="kay.mann@enron.com",
        recipients=["bob@enron.com"],
        subject="Contract draft",
        body="Please see attached. Thanks, Kay",
        timestamp=datetime(2001, 5, 1, tzinfo=timezone.utc),
        folder="mann-k/sent",
    )
    assert msg.sender == "kay.mann@enron.com"
    assert EmailMessage.model_validate(msg.model_dump()) == msg


def test_evaluation_result_rejects_bad_decision():
    with pytest.raises(ValidationError):
        EvaluationResult(
            style_score=0.9, groundedness_score=0.6, confidence_score=0.8,
            final_score=0.79, hedge_count=0, decision="maybe",
        )


def test_scores_clamped_to_unit_interval():
    with pytest.raises(ValidationError):
        EvaluationResult(
            style_score=1.5, groundedness_score=0.6, confidence_score=0.8,
            final_score=0.79, hedge_count=0, decision="deliver",
        )


def test_retrieved_chunk_and_clone_response():
    chunk = KnowledgeChunk(content="TCP is...", source_topic="Networking",
                           source_field="Computer science", chunk_index=0)
    retrieved = RetrievedChunk(chunk=chunk, similarity=0.82)
    resp = CloneResponse(
        query="what is tcp?", delivered=True, response_text="Hi, ...",
        citations=["[1] Networking (chunk 0)"], evaluation=None,
        fallback=None, latency_seconds=0.12,
    )
    assert retrieved.chunk.source_topic == "Networking"
    assert resp.delivered is True


def test_style_profile_serializes():
    p = StyleProfile(
        employee_name="kay_mann",
        style_features={"message_length": 85.3},
        style_vector=[0.1, -0.2],
        greeting_patterns={"Hi": 0.4},
        signoff_patterns={"Thanks": 0.5},
        common_phrases=["please let me know"],
        n_emails=200,
        last_updated=datetime.now(timezone.utc),
    )
    assert StyleProfile.model_validate_json(p.model_dump_json()).n_emails == 200


def test_fallback_response_fields():
    fb = FallbackResponse(
        trigger_reason="low_confidence",
        context_summary="User asked about dark matter; no relevant chunks.",
        calendar_link="https://calendly.com/kay_mann/30min",
        available_slots=["2026-07-06 10:00", "2026-07-06 14:00"],
    )
    assert fb.trigger_reason == "low_confidence"
    assert len(fb.available_slots) == 2
