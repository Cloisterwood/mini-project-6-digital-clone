from digital_clone.config import CloneConfig


def test_config_defaults():
    cfg = CloneConfig()
    assert cfg.style_weight == 0.4
    assert cfg.groundedness_weight == 0.4
    assert cfg.confidence_weight == 0.2
    assert cfg.fallback_threshold == 0.75
    assert cfg.alpha == 0.3
    assert cfg.chunk_size == 500
    assert cfg.chunk_overlap == 50
    assert cfg.employee_email == "kay.mann@enron.com"


def test_config_is_overridable():
    cfg = CloneConfig(fallback_threshold=0.70)
    assert cfg.fallback_threshold == 0.70
