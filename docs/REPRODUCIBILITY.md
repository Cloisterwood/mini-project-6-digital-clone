# Reproducibility

Everything needed to rebuild this project's artifacts from a clean clone: dataset identities and hashes, the exact environment, rebuild commands, and what is — and is not — bit-reproducible.

## Environment (build machine)

| Item | Value |
|---|---|
| Machine | Apple MacBook, Apple M2, 24 GB RAM, macOS (arm64) |
| Python | **3.14.5** (Homebrew `python3.14`, `.venv`) |
| Install date | 2026-10-07 |

Exact installed versions the artifacts were built with (`pip freeze` subset):

```
pydantic==2.13.5
numpy==2.5.3
scikit-learn==1.9.1
faiss-cpu==1.15.1
sentence-transformers==6.1.0
torch==2.14.1
transformers==5.19.0
langchain-text-splitters==1.1.3
datasets==5.1.0
kagglehub==1.0.2
pandas==3.0.6
matplotlib==3.11.2
seaborn==0.13.2
joblib==1.6.0
pytest==9.1.1
pytest-cov==7.1.0
```

`requirements.txt` pins minimum versions (`>=`); the versions above are what the committed artifacts were actually produced with. Embedding models can drift across `sentence-transformers`/`torch` releases, so if you need scores to match to the third decimal, install these exact versions.

**CrewAI (optional path only):** every crewai release up to 1.15.24 requires Python `>=3.10,<3.14`, so it cannot install into the 3.14.5 `.venv`. Verified separately on a Python **3.13.5** side-venv: `pip install crewai` resolved to **crewai 1.15.24**, and `digital_clone.crew.build_crew()` with `OPENAI_API_KEY` set constructed a real 5-agent `crewai.Crew` (2026-10-07). This path is not exercised by the graded pipeline, the tests, or the CLI.

## Datasets

### Enron email corpus (style learning)

| Property | Value |
|---|---|
| Source | Kaggle `wcukierski/enron-email-dataset`, version 2, via `kagglehub.dataset_download("wcukierski/enron-email-dataset")` |
| File | `emails.csv` (columns `file`, `message`), ~358 MB |
| SHA-256 | `a605f0a2ca4a4feaa557eb0f2be825914906dca816066d7e58983e7e2e8bd274` (computed 2026-10-07 on the cached download at `~/.cache/kagglehub/datasets/wcukierski/enron-email-dataset/versions/2/emails.csv`) |
| Cache | kagglehub caches the download; a second build does not re-download |
| License | The underlying corpus is the Enron email dataset released by FERC as public record; the Kaggle mirror carries its own dataset-page terms. Consult the Kaggle page before redistributing data or derivatives. This repository commits only derived numeric profiles, never the raw corpus. |

Used by: `scripts/build_style_profile.py` (folder `mann-k`, sender `kay.mann@enron.com`; 8,926 raw sent-folder messages → 7,414 usable after cleaning).

### Textbook knowledge base (RAG)

| Property | Value |
|---|---|
| Source | HuggingFace `open-phi/textbooks`, streamed |
| Revision | `292aaae99cbecacad50f692d7327887f05dacaf2` — the dataset's `lastModified` is 2023-10-08, i.e. unchanged since well before the 2026-10-07 build, so this pinned revision is the revision used |
| Filter | `field` containing "computer" (the `computer_science` field dominates the dataset); first 500 books in stream order (`min_docs=500` diversity floor — see iteration log Stage 3 notes) |
| License | No machine-readable license tag is exposed on the dataset's API metadata; consult the dataset page before redistributing content. This repository commits only chunk counts and similarity scores, never the text. |

Used by: `scripts/build_knowledge_base.py` (chunk 500/50 → 210,225 chunks, MiniLM embeddings, FAISS `IndexFlatIP`).

### Embedding model

`sentence-transformers/all-MiniLM-L6-v2`, fetched from the HuggingFace hub on first use and cached locally (`~/.cache/huggingface/`). All vectors are L2-normalized before add and search; FAISS `IndexFlatIP` on normalized vectors is exact cosine similarity.

## Rebuild commands

From a clean clone (see README "Setup" for venv creation):

```bash
.venv/bin/python scripts/build_style_profile.py      # ~seconds (cached corpus); profile → data/models/
.venv/bin/python scripts/build_knowledge_base.py     # measured 528.6 s indexing on the build machine
.venv/bin/pytest                                     # 81 tests, offline, no artifacts needed
.venv/bin/python -m digital_clone.cli --query "What is TCP/IP?"   # smoke (~10 s model+index load, then ms/query)

# Evaluation — delete a stale decision log first; the planner appends to it:
rm -f data/evaluations/decision_log.jsonl
.venv/bin/python scripts/run_evaluation.py           # 20 queries, regenerates docs/evaluation_report.md
.venv/bin/python scripts/make_visualizations.py      # 6 PNGs → docs/visualizations/
```

Expected outputs and their measured values on the build machine: style profile from 7,414 emails; 210,225 chunks from 500 books; 5/5 retrieval spot checks relevant (top-1 similarity 0.78–0.86, 13–62 ms); evaluation → 100% reliability, fallback rate 40%, style 0.999, groundedness 0.648, confidence 0.728, in-domain final 0.881.

## What reproduces exactly — and what doesn't

**Deterministic (same versions/hardware):** every score in `data/evaluations/` and `docs/evaluation_report.md`. Style features, EMA learning, retrieval (exact FAISS flat search), answer templates, evaluation arithmetic, and the deliver/fallback decision have no RNG and no network dependence at query time. The Stage 7 verification relied on this: a default-config rerun reproduced the kept experiment's scores exactly. Offline tests use `HashEmbedder`, so the suite needs no model download.

**Varies run to run:** latency numbers (hardware/thermal; measured 13–62 ms retrieval, ~52 ms mean end-to-end on the build machine) and absolute indexing wall-clock (528.6 s here; scale with CPU, not with the algorithm).

**Depends on pinned sources:** the chunk set depends on the HF stream order of `open-phi/textbooks` at the pinned revision (rebuilds after an upstream dataset change could select different books — re-check the revision hash above). The Enron build depends on the Kaggle CSV hash above. The MiniLM model itself is fetched from the HF hub; a changed model revision upstream would change embeddings — pin `sentence-transformers`/`transformers` versions if scores must match exactly.

**Known gotchas:** `decision_log.jsonl` is append-only (delete before a fresh evaluation run); the large artifacts `data/rag/faiss_index/index.faiss` (308 MB) and `chunks_metadata.json` (102 MB) are gitignored and rebuilt by `build_knowledge_base.py`; the style learner's `data/models/*.joblib` is likewise gitignored, and `build_planner` loads both the committed JSON profile and that joblib — so on a clean clone, run `build_style_profile.py` before the CLI or evaluation.
