from digital_clone.agents.style_agent import ChatStyleAgent
from digital_clone.config import CloneConfig


def make_agent(tmp_path, **overrides):
    cfg = CloneConfig(data_dir=tmp_path, batch_size=4, pca_components=3, **overrides)
    return ChatStyleAgent(cfg)


def test_learn_builds_profile(tmp_path, sample_emails):
    agent = make_agent(tmp_path)
    profile = agent.learn(sample_emails)
    assert profile.n_emails == len(sample_emails)
    assert len(profile.style_features) == 13
    assert len(profile.style_vector) >= 1
    assert profile.greeting_patterns  # learned "hi"


def test_learn_is_incremental(tmp_path, sample_emails):
    agent = make_agent(tmp_path)
    agent.learn(sample_emails)
    # 12 fixture emails / batch_size 4 = 3 batches
    assert len(agent.learner.history) == 3


def test_style_score_high_for_matching_text(tmp_path, sample_emails):
    agent = make_agent(tmp_path)
    agent.learn(sample_emails)
    on_style = "Hi Ben,\n\nPlease review the agreement draft... Can you confirm?\n\nThanks,\nKay"
    off_style = "YO!!! CHECK THIS OUT NOW!!! amazing stuff lol"
    assert agent.style_score(on_style) > agent.style_score(off_style)
    assert 0.0 <= agent.style_score(on_style) <= 1.0


def test_apply_style_adds_greeting_and_signoff(tmp_path, sample_emails):
    agent = make_agent(tmp_path)
    agent.learn(sample_emails)
    styled = agent.apply_style("TCP is a connection-oriented transport protocol.")
    assert styled.lower().startswith("hi")
    assert "kay" in styled.lower()


def test_save_and_load_roundtrip(tmp_path, sample_emails):
    agent = make_agent(tmp_path)
    agent.learn(sample_emails)
    agent.save()
    fresh = make_agent(tmp_path)
    loaded = fresh.load()
    assert loaded.n_emails == len(sample_emails)
    assert 0.0 <= fresh.style_score("Hi Ben,\n\nQuick note.\n\nThanks,\nKay") <= 1.0
