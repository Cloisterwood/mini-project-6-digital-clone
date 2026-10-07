"""Agent 1: learns and applies the employee's communication style."""
from datetime import datetime, timezone
from typing import Optional

import numpy as np

from digital_clone.config import CloneConfig
from digital_clone.models import EmailMessage, StyleProfile
from digital_clone.style.features import (
    FEATURE_NAMES,
    build_feature_matrix,
    cosine,
    extract_email_features,
    extract_style_metadata,
    features_to_array,
)
from digital_clone.style.incremental import IncrementalStyleLearner


class ChatStyleAgent:
    def __init__(self, config: CloneConfig):
        self.config = config
        self.learner = IncrementalStyleLearner(
            alpha=config.alpha, n_components=config.pca_components)
        self.profile: Optional[StyleProfile] = None

    def learn(self, emails: list[EmailMessage]) -> StyleProfile:
        bodies = [e.body for e in emails]
        for start in range(0, len(bodies), self.config.batch_size):
            batch = bodies[start:start + self.config.batch_size]
            self.learner.partial_fit(build_feature_matrix(batch))
        mean_features = build_feature_matrix(bodies).mean(axis=0)
        meta = extract_style_metadata(bodies)
        self.profile = StyleProfile(
            employee_name=self.config.employee_name,
            style_features=dict(zip(FEATURE_NAMES, mean_features.tolist())),
            style_vector=self.learner.profile_vector.tolist(),
            greeting_patterns=meta["greeting_patterns"],
            signoff_patterns=meta["signoff_patterns"],
            common_phrases=meta["common_phrases"],
            n_emails=len(emails),
            last_updated=datetime.now(timezone.utc),
        )
        return self.profile

    def style_score(self, text: str) -> float:
        if self.profile is None:
            return 0.0
        response_vec = features_to_array(extract_email_features(text))
        profile_vec = np.array([self.profile.style_features[n] for n in FEATURE_NAMES])
        return float(np.clip(cosine(response_vec, profile_vec), 0.0, 1.0))

    def apply_style(self, body: str) -> str:
        greeting = "Hi"
        signoff = "Thanks"
        if self.profile:
            if self.profile.greeting_patterns:
                greeting = max(self.profile.greeting_patterns,
                               key=self.profile.greeting_patterns.get).capitalize()
            if self.profile.signoff_patterns:
                signoff = max(self.profile.signoff_patterns,
                              key=self.profile.signoff_patterns.get).capitalize()
        first_name = self.config.employee_name.split("_")[0].capitalize()
        return f"{greeting},\n\n{body}\n\n{signoff},\n{first_name}"

    def save(self) -> None:
        path = self.config.style_profile_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.profile.model_dump_json(indent=2))
        self.learner.save(path.with_suffix(".joblib"))

    def load(self) -> StyleProfile:
        path = self.config.style_profile_path
        self.profile = StyleProfile.model_validate_json(path.read_text())
        self.learner = IncrementalStyleLearner.load(path.with_suffix(".joblib"))
        return self.profile
