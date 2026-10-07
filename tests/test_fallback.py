import pytest

from digital_clone.agents.fallback_agent import FallbackAgent
from digital_clone.config import CloneConfig
from digital_clone.models import EvaluationResult


def make_eval(final=0.8, hedges=0):
    return EvaluationResult(style_score=0.9, groundedness_score=0.7,
                            confidence_score=0.8, final_score=final,
                            hedge_count=hedges, decision="deliver")


def agent():
    return FallbackAgent(CloneConfig())


def test_no_fallback_on_good_score():
    assert agent().should_fallback("what is tcp?", make_eval(final=0.85)) is None


def test_system_error_has_priority():
    reason = agent().should_fallback("what is tcp?", make_eval(final=0.9),
                                     error=RuntimeError("index missing"))
    assert reason == "system_error"


def test_user_booking_request_detected():
    assert agent().should_fallback("Can we schedule a call?", make_eval(0.9)) == "user_request"
    assert agent().should_fallback("I'd like to talk to someone", make_eval(0.9)) == "user_request"


def test_low_score_triggers():
    assert agent().should_fallback("q", make_eval(final=0.6)) == "low_confidence"


def test_hedging_triggers_even_with_passing_score():
    assert agent().should_fallback("q", make_eval(final=0.8, hedges=4)) == "high_uncertainty"


def test_build_response_contents():
    fb = agent().build_response("explain dark matter", make_eval(final=0.5),
                                reason="low_confidence")
    assert fb.trigger_reason == "low_confidence"
    assert "dark matter" in fb.context_summary
    assert fb.calendar_link.startswith("https://calendly.com/kay_mann")
    assert len(fb.available_slots) == 6


# --- Stage 4 additions: threshold boundaries (prep for S7 tuning) -----------

@pytest.mark.parametrize("threshold", [0.70, 0.75, 0.80])
def test_low_confidence_boundary_tracks_threshold(threshold):
    fb = FallbackAgent(CloneConfig(fallback_threshold=threshold))
    assert fb.should_fallback("q", make_eval(final=threshold)) is None
    assert fb.should_fallback("q", make_eval(final=threshold - 0.01)) == "low_confidence"


def test_trigger_priority_order():
    # system_error > user_request > low_confidence > high_uncertainty
    fb = agent()
    assert fb.should_fallback("schedule a call", make_eval(final=0.6, hedges=9),
                              error=RuntimeError()) == "system_error"
    assert fb.should_fallback("schedule a call", make_eval(final=0.6, hedges=9)) == "user_request"
    assert fb.should_fallback("q", make_eval(final=0.6, hedges=9)) == "low_confidence"
    assert fb.should_fallback("q", make_eval(final=0.9, hedges=9)) == "high_uncertainty"


def test_build_response_uses_config_calendar_template():
    fb = FallbackAgent(CloneConfig(
        calendar_link_template="https://cal.example/{employee_name}/30min"))
    resp = fb.build_response("q", None, reason="system_error")
    assert resp.calendar_link == "https://cal.example/kay_mann/30min"


def test_build_response_without_evaluation():
    fb = agent().build_response("q", None, reason="system_error")
    assert "no evaluation available" in fb.context_summary
    assert fb.trigger_reason == "system_error"
    assert len(fb.available_slots) == 6


def test_slots_skip_weekends_and_use_weekday_times():
    from datetime import datetime

    slots = agent()._slots(now=datetime(2026, 10, 7, 9, 0))  # a Wednesday
    assert len(slots) == 6
    days = [s.split()[0] for s in slots]
    # Next 3 weekdays: Thu Oct 8, Fri Oct 9, Mon Oct 12
    assert days == ["2026-10-08", "2026-10-08", "2026-10-09",
                    "2026-10-09", "2026-10-12", "2026-10-12"]
    times = {s.split()[1] for s in slots}
    assert times == {"10:00", "14:00"}
