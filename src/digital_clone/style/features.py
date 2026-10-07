"""13 numeric style features per email + non-scalar style metadata."""
import re
from collections import Counter

import numpy as np

FEATURE_NAMES = [
    "message_length", "greeting_presence", "signoff_presence",
    "ellipsis_rate", "exclamation_rate", "dash_rate",
    "capitalization_ratio", "question_frequency", "vocabulary_richness",
    "reasoning_rate", "sentiment_polarity", "formality_score",
    "technical_term_rate",
]

GREETINGS = ["hi", "hello", "dear", "hey", "good morning", "good afternoon"]
SIGNOFFS = ["thanks", "thank you", "regards", "best", "sincerely", "cheers"]
REASONING_WORDS = {"because", "therefore", "however", "thus", "since",
                   "consequently", "accordingly"}
POSITIVE_WORDS = {"good", "great", "thanks", "appreciate", "happy", "glad",
                  "excellent", "perfect", "pleased"}
NEGATIVE_WORDS = {"problem", "issue", "concern", "sorry", "unfortunately",
                  "wrong", "fail", "risk", "bad"}
FORMAL_WORDS = {"please", "kindly", "regards", "pursuant", "attached",
                "hereby", "regarding", "sincerely"}
INFORMAL_WORDS = {"gonna", "wanna", "yeah", "ok", "okay", "cool", "stuff",
                  "hey", "btw"}
TECHNICAL_TERMS = {"contract", "agreement", "counterparty", "draft", "legal",
                   "system", "data", "network", "protocol", "server",
                   "model", "analysis", "process", "algorithm", "database"}


def _words(text: str) -> list[str]:
    return re.findall(r"[A-Za-z']+", text.lower())


def _per_100_words(count: int, n_words: int) -> float:
    return 100.0 * count / max(n_words, 1)


def extract_email_features(text: str) -> dict[str, float]:
    words = _words(text)
    n = len(words)
    lowered = text.lower()
    first_line = lowered.strip().splitlines()[0] if lowered.strip() else ""
    last_lines = " ".join(lowered.strip().splitlines()[-3:])
    letters = [c for c in text if c.isalpha()]
    upper = sum(1 for c in letters if c.isupper())
    contractions = len(re.findall(r"\b\w+'(?:s|t|re|ll|ve|d)\b", lowered))
    formal = sum(1 for w in words if w in FORMAL_WORDS)
    informal = sum(1 for w in words if w in INFORMAL_WORDS) + contractions

    return {
        "message_length": float(n),
        "greeting_presence": 1.0 if any(first_line.startswith(g) for g in GREETINGS) else 0.0,
        "signoff_presence": 1.0 if any(s in last_lines for s in SIGNOFFS) else 0.0,
        "ellipsis_rate": _per_100_words(text.count("..."), n),
        "exclamation_rate": _per_100_words(text.count("!"), n),
        "dash_rate": _per_100_words(text.count("--") + text.count(" - "), n),
        "capitalization_ratio": upper / max(len(letters), 1),
        "question_frequency": float(text.count("?")),
        "vocabulary_richness": len(set(words)) / max(n, 1),
        "reasoning_rate": _per_100_words(sum(1 for w in words if w in REASONING_WORDS), n),
        "sentiment_polarity": (sum(1 for w in words if w in POSITIVE_WORDS)
                               - sum(1 for w in words if w in NEGATIVE_WORDS)) / max(n, 1),
        "formality_score": formal / max(formal + informal, 1),
        "technical_term_rate": _per_100_words(sum(1 for w in words if w in TECHNICAL_TERMS), n),
    }


def features_to_array(features: dict[str, float]) -> np.ndarray:
    return np.array([features[name] for name in FEATURE_NAMES], dtype=np.float64)


def build_feature_matrix(bodies: list[str]) -> np.ndarray:
    return np.vstack([features_to_array(extract_email_features(b)) for b in bodies])


def extract_style_metadata(bodies: list[str]) -> dict:
    greeting_counts: Counter = Counter()
    signoff_counts: Counter = Counter()
    phrase_counts: Counter = Counter()
    for body in bodies:
        lowered = body.lower().strip()
        first_line = lowered.splitlines()[0] if lowered else ""
        last_lines = " ".join(lowered.splitlines()[-3:])
        for g in GREETINGS:
            if first_line.startswith(g):
                greeting_counts[g] += 1
                break
        for s in SIGNOFFS:
            if s in last_lines:
                signoff_counts[s] += 1
                break
        words = _words(body)
        for i in range(len(words) - 2):
            phrase_counts[" ".join(words[i:i + 3])] += 1
    n = max(len(bodies), 1)
    return {
        "greeting_patterns": {g: c / n for g, c in greeting_counts.most_common(5)},
        "signoff_patterns": {s: c / n for s, c in signoff_counts.most_common(5)},
        "common_phrases": [p for p, c in phrase_counts.most_common(10) if c > 1],
    }


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    denom = float(np.linalg.norm(a) * np.linalg.norm(b))
    if denom == 0.0:
        return 0.0
    return float(np.dot(a, b) / denom)
