"""Incremental style profile: StandardScaler + PCA fit on the first batch,
then EMA updates: profile = (1 - alpha) * profile + alpha * batch_vector.

Persistence uses joblib (pickle-based) ONLY for artifacts this program writes
itself under data/models/ — never for files from untrusted sources. sklearn
transformers have no JSON-safe serialization, so this is the standard approach;
the profile's human-readable content is separately stored as JSON (StyleProfile)."""
from pathlib import Path
from typing import Optional

import joblib
import numpy as np
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler


class IncrementalStyleLearner:
    def __init__(self, alpha: float = 0.3, n_components: int = 6):
        self.alpha = alpha
        self.n_components = n_components
        self.scaler = StandardScaler()
        self.pca: Optional[PCA] = None
        self.profile_vector: Optional[np.ndarray] = None
        self.history: list[np.ndarray] = []
        self._fitted = False

    def partial_fit(self, matrix: np.ndarray) -> np.ndarray:
        if not self._fitted:
            n_comp = min(self.n_components, matrix.shape[0], matrix.shape[1])
            self.pca = PCA(n_components=n_comp)
            reduced = self.pca.fit_transform(self.scaler.fit_transform(matrix))
            self._fitted = True
        else:
            reduced = self.transform(matrix)
        batch_vector = reduced.mean(axis=0)
        if self.profile_vector is None:
            self.profile_vector = batch_vector
        else:
            self.profile_vector = (1 - self.alpha) * self.profile_vector + self.alpha * batch_vector
        self.history.append(self.profile_vector.copy())
        return self.profile_vector

    def transform(self, matrix: np.ndarray) -> np.ndarray:
        if not self._fitted:
            raise RuntimeError("Learner not fitted; call partial_fit first.")
        return self.pca.transform(self.scaler.transform(matrix))

    def save(self, path: Path) -> None:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        joblib.dump({
            "alpha": self.alpha, "n_components": self.n_components,
            "scaler": self.scaler, "pca": self.pca,
            "profile_vector": self.profile_vector, "history": self.history,
            "fitted": self._fitted,
        }, path)

    @classmethod
    def load(cls, path: Path) -> "IncrementalStyleLearner":
        state = joblib.load(path)
        learner = cls(alpha=state["alpha"], n_components=state["n_components"])
        learner.scaler = state["scaler"]
        learner.pca = state["pca"]
        learner.profile_vector = state["profile_vector"]
        learner.history = state["history"]
        learner._fitted = state["fitted"]
        return learner
