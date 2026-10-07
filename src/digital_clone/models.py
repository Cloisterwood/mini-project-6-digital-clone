from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field

UnitFloat = Field(ge=0.0, le=1.0)


class EmailMessage(BaseModel):
    sender: str
    recipients: list[str] = []
    subject: str = ""
    body: str
    timestamp: Optional[datetime] = None
    folder: str = ""


class StyleProfile(BaseModel):
    employee_name: str
    style_features: dict[str, float]          # mean raw features (13 keys)
    style_vector: list[float]                 # scaler+PCA EMA profile vector
    greeting_patterns: dict[str, float] = {}
    signoff_patterns: dict[str, float] = {}
    common_phrases: list[str] = []
    n_emails: int = 0
    last_updated: datetime


class KnowledgeChunk(BaseModel):
    content: str
    source_topic: str
    source_field: str
    chunk_index: int


class RetrievedChunk(BaseModel):
    chunk: KnowledgeChunk
    similarity: float


class EvaluationResult(BaseModel):
    style_score: float = UnitFloat
    groundedness_score: float = UnitFloat
    confidence_score: float = UnitFloat
    final_score: float = UnitFloat
    hedge_count: int = 0
    decision: Literal["deliver", "fallback"]


class FallbackResponse(BaseModel):
    trigger_reason: str
    context_summary: str
    calendar_link: str
    available_slots: list[str] = []


class CloneResponse(BaseModel):
    query: str
    delivered: bool
    response_text: Optional[str] = None
    citations: list[str] = []
    evaluation: Optional[EvaluationResult] = None
    fallback: Optional[FallbackResponse] = None
    latency_seconds: float = 0.0
