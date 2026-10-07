from pathlib import Path

from pydantic import BaseModel


class CloneConfig(BaseModel):
    """Every tunable in the system. Never hardcode these at call sites."""

    # Employee / style learning
    employee_email: str = "kay.mann@enron.com"
    employee_name: str = "kay_mann"
    employee_folder: str = "mann-k"      # Kaggle corpus folder prefix
    alpha: float = 0.3                    # incremental learning rate
    batch_size: int = 50
    pca_components: int = 6

    # Evaluation weights + thresholds
    style_weight: float = 0.4
    groundedness_weight: float = 0.4
    confidence_weight: float = 0.2
    fallback_threshold: float = 0.75
    hedge_fallback_count: int = 3
    expected_response_length: int = 400   # chars, for completeness score
    # Confidence formula weights (02-SYSTEM-CONTRACT tension #1). Kept S7
    # reweight 0.6/0.4 (iteration log Entry 2); the spec formula 0.5/0.3 caps
    # confidence at 0.8 and measured 0.572 at baseline.
    confidence_relevance_weight: float = 0.6
    confidence_completeness_weight: float = 0.4

    # RAG
    chunk_size: int = 500
    chunk_overlap: int = 50
    top_k: int = 5
    min_chunks: int = 900

    # Fallback booking (02-SYSTEM-CONTRACT fixed default; S4 consumes the template)
    calendar_link_template: str = "https://calendly.com/{employee_name}/30min"

    # Paths
    data_dir: Path = Path("data")

    @property
    def style_profile_path(self) -> Path:
        return self.data_dir / "models" / f"style_profile_{self.employee_name}.json"

    @property
    def rag_dir(self) -> Path:
        return self.data_dir / "rag"

    @property
    def eval_dir(self) -> Path:
        return self.data_dir / "evaluations"
