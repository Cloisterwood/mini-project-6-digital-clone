import numpy as np
import pytest

from digital_clone.style.incremental import IncrementalStyleLearner

rng = np.random.default_rng(42)


def make_batch(n=20, shift=0.0):
    return rng.normal(loc=shift, scale=1.0, size=(n, 13))


def test_first_batch_sets_profile():
    learner = IncrementalStyleLearner(alpha=0.3, n_components=4)
    vec = learner.partial_fit(make_batch())
    assert vec.shape == (4,)
    assert learner.profile_vector is not None
    assert len(learner.history) == 1


def test_ema_update_formula():
    learner = IncrementalStyleLearner(alpha=0.3, n_components=4)
    v1 = learner.partial_fit(make_batch()).copy()
    b2 = make_batch(shift=2.0)
    scaled = learner.scaler.transform(b2)
    expected_batch_vec = learner.pca.transform(scaled).mean(axis=0)
    v2 = learner.partial_fit(b2)
    np.testing.assert_allclose(v2, 0.7 * v1 + 0.3 * expected_batch_vec, rtol=1e-9)
    assert len(learner.history) == 2


def test_components_capped_by_samples():
    learner = IncrementalStyleLearner(alpha=0.3, n_components=10)
    vec = learner.partial_fit(make_batch(n=3))  # only 3 samples
    assert vec.shape[0] <= 3


def test_transform_before_fit_raises():
    with pytest.raises(RuntimeError):
        IncrementalStyleLearner().transform(make_batch())


def test_save_and_load_roundtrip(tmp_path):
    learner = IncrementalStyleLearner(alpha=0.3, n_components=4)
    learner.partial_fit(make_batch())
    p = tmp_path / "learner.joblib"
    learner.save(p)
    loaded = IncrementalStyleLearner.load(p)
    np.testing.assert_allclose(loaded.profile_vector, learner.profile_vector)
    assert loaded.alpha == 0.3
