import math

import numpy as np

from digital_clone.style.features import (
    FEATURE_NAMES,
    build_feature_matrix,
    cosine,
    extract_email_features,
    extract_style_metadata,
    features_to_array,
)

SAMPLE = (
    "Hi Bob,\n\nPlease review the attached contract because we need it "
    "signed by Friday... Can you confirm? However, the counterparty may "
    "push back!\n\nThanks,\nKay"
)


def test_thirteen_features_extracted():
    feats = extract_email_features(SAMPLE)
    assert set(feats.keys()) == set(FEATURE_NAMES)
    assert len(FEATURE_NAMES) == 13
    assert all(math.isfinite(v) for v in feats.values())


def test_specific_feature_values():
    feats = extract_email_features(SAMPLE)
    assert feats["greeting_presence"] == 1.0          # "Hi"
    assert feats["signoff_presence"] == 1.0           # "Thanks"
    assert feats["question_frequency"] == 1.0         # one "?"
    assert feats["ellipsis_rate"] > 0                 # "..."
    assert feats["exclamation_rate"] > 0              # "!"
    assert feats["reasoning_rate"] > 0                # because, however
    assert 0 < feats["vocabulary_richness"] <= 1


def test_empty_text_is_safe():
    feats = extract_email_features("")
    assert all(math.isfinite(v) for v in feats.values())


def test_features_to_array_order():
    feats = extract_email_features(SAMPLE)
    arr = features_to_array(feats)
    assert arr.shape == (13,)
    assert arr[0] == feats["message_length"]


def test_build_feature_matrix():
    m = build_feature_matrix([SAMPLE, "Short note.", ""])
    assert m.shape == (3, 13)


def test_style_metadata():
    meta = extract_style_metadata([SAMPLE, "Hi team,\nUpdate attached.\nThanks,\nKay"])
    assert meta["greeting_patterns"].get("hi", 0) == 1.0
    assert "thanks" in meta["signoff_patterns"]
    assert isinstance(meta["common_phrases"], list)


def test_cosine():
    a, b = np.array([1.0, 0.0]), np.array([1.0, 0.0])
    assert cosine(a, b) == 1.0
    assert cosine(a, np.array([0.0, 0.0])) == 0.0  # zero vector safe
