"""Agent 4: graceful degradation to a calendar booking."""
from datetime import datetime, timedelta
from typing import Optional

from digital_clone.config import CloneConfig
from digital_clone.models import EvaluationResult, FallbackResponse

BOOKING_PHRASES = ["schedule a call", "schedule a meeting", "book a call",
                   "book a meeting", "talk to someone", "speak to someone",
                   "set up a call", "talk directly", "human"]


class FallbackAgent:
    def __init__(self, config: CloneConfig):
        self.config = config

    def should_fallback(self, query: str,
                        evaluation: Optional[EvaluationResult],
                        error: Optional[Exception] = None) -> Optional[str]:
        if error is not None:
            return "system_error"
        if any(p in query.lower() for p in BOOKING_PHRASES):
            return "user_request"
        if evaluation is None or evaluation.final_score < self.config.fallback_threshold:
            return "low_confidence"
        if evaluation.hedge_count > self.config.hedge_fallback_count:
            return "high_uncertainty"
        return None

    def _slots(self, now: Optional[datetime] = None) -> list[str]:
        now = now or datetime.now()
        slots, day = [], now
        while len(slots) < 6:
            day += timedelta(days=1)
            if day.weekday() >= 5:  # skip weekends
                continue
            for hour in (10, 14):
                slots.append(day.strftime(f"%Y-%m-%d {hour:02d}:00"))
        return slots[:6]

    def build_response(self, query: str,
                       evaluation: Optional[EvaluationResult],
                       reason: str) -> FallbackResponse:
        score_txt = (f"final score {evaluation.final_score:.2f} "
                     f"(style {evaluation.style_score:.2f}, "
                     f"groundedness {evaluation.groundedness_score:.2f}, "
                     f"confidence {evaluation.confidence_score:.2f})"
                     if evaluation else "no evaluation available")
        summary = (f"You asked: \"{query}\". I couldn't answer this confidently "
                   f"({reason}; {score_txt}), so let's set up time to discuss it directly.")
        return FallbackResponse(
            trigger_reason=reason,
            context_summary=summary,
            calendar_link=self.config.calendar_link_template.format(
                employee_name=self.config.employee_name),
            available_slots=self._slots(),
        )
