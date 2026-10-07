"""Environment self-check: `python -m digital_clone doctor`.

Stage 1 acceptance requires this to pass: interpreter/package versions,
import checks, disk space, and a fixture-free smoke of numpy/sklearn/faiss.
No GPU detection — everything in this project runs on CPU.
"""

import importlib
import importlib.metadata
import platform
import shutil
import sys

# (distribution name for importlib.metadata, module name for import smoke)
PACKAGES = [
    ("pydantic", "pydantic"),
    ("numpy", "numpy"),
    ("scikit-learn", "sklearn"),
    ("faiss-cpu", "faiss"),
    ("sentence-transformers", "sentence_transformers"),
    ("langchain-text-splitters", "langchain_text_splitters"),
    ("datasets", "datasets"),
    ("kagglehub", "kagglehub"),
    ("pandas", "pandas"),
    ("matplotlib", "matplotlib"),
    ("seaborn", "seaborn"),
    ("joblib", "joblib"),
    ("pytest", "pytest"),
    ("pytest-cov", "pytest_cov"),
]


def _check_versions() -> list[tuple[str, str]]:
    rows = []
    for dist, module in PACKAGES:
        try:
            rows.append((dist, importlib.metadata.version(dist)))
        except importlib.metadata.PackageNotFoundError:
            rows.append((dist, "MISSING"))
    return rows


def _smoke() -> list[str]:
    """Fixture-free smoke: import the heavy stack and run one trivial op each."""
    problems = []

    import numpy as np

    if int(np.array([1, 2, 3]).sum()) != 6:
        problems.append("numpy: basic array op returned an unexpected result")

    from sklearn.decomposition import PCA
    from sklearn.preprocessing import StandardScaler

    import faiss

    vectors = np.array([[1.0, 0.0], [0.0, 1.0]], dtype="float32")
    faiss.normalize_L2(vectors)
    index = faiss.IndexFlatIP(vectors.shape[1])
    index.add(vectors)
    scores, _ = index.search(vectors[:1], 1)
    if not (0.99 <= float(scores[0][0]) <= 1.01):
        problems.append(f"faiss: self-similarity search gave {scores[0][0]}")

    scaler = StandardScaler().fit(vectors)
    PCA(n_components=1).fit_transform(scaler.transform(vectors))

    return problems


def run_doctor() -> int:
    print("digital_clone doctor")
    print(f"  interpreter : Python {sys.version.split()[0]} at {sys.executable}")
    print(f"  platform    : {platform.platform()}")

    total, _, free = shutil.disk_usage(".")
    free_gb = free / 1e9
    print(f"  disk (cwd)  : {free_gb:.1f} GB free of {total / 1e9:.0f} GB")

    print("  packages:")
    problems = []
    for dist, version in _check_versions():
        print(f"    {dist:<24} {version}")
        if version == "MISSING":
            problems.append(f"{dist}: not installed")

    try:
        smoke_problems = _smoke()
        print(f"  smoke       : numpy/sklearn/faiss imports + ops OK"
              if not smoke_problems else f"  smoke       : {smoke_problems}")
        problems.extend(smoke_problems)
    except Exception as exc:  # noqa: BLE001 - doctor must report, not crash
        problems.append(f"smoke failed: {type(exc).__name__}: {exc}")
        print(f"  smoke       : FAILED ({type(exc).__name__}: {exc})")

    if problems:
        print("\ndoctor: FAIL")
        for problem in problems:
            print(f"  - {problem}")
        return 1
    print("\ndoctor: OK")
    return 0
