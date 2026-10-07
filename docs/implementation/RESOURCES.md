# Resources — confirmed and to-confirm

## Confirmed (2026-10-06)

- **GitHub account:** `Cloisterwood` (gh CLI authenticated on this Mac; token has `repo` scope). Repo to be created in S0 — proposed name `mini-project-6-digital-clone`, **private**. Record final name/URL/visibility here after S0.
- **Datasets (resolved by the July plan; no links needed from the user):**
  - Enron corpus: Kaggle `wcukierski/enron-email-dataset` (~358 MB ZIP; `emails.csv` with columns `file`, `message`) via `kagglehub.dataset_download` — public, no Kaggle credentials required.
  - Textbooks: HuggingFace `open-phi/textbooks` (streamed; filter `field` containing "computer"; columns `markdown`, `topic`, `field`).
- **Hardware:** Apple M2, 24 GB — sufficient for the entire pipeline on CPU; no Colab/RunPod expected.
- **Implementation reference:** `docs/superpowers/plans/2026-07-04-enron-digital-clone.md` (Tasks 1–16 with code and tests).

## Stage 0 record (2026-10-07)

- **GitHub repo:** https://github.com/Cloisterwood/mini-project-6-digital-clone (private, under `Cloisterwood`). First pushed commit `a367683319b61962cc615f2692332fab1c866ff2`; remote SHA verified equal to local HEAD.
- **Runner/model for S0:** ZCode session, model GLM-5.3-Flash. Sol/Terra/Luna tier table not applicable (VS Code-only, per 03-OPERATING-RULES).
- **Linear (user decision 2026-10-07):** the user creates the ten stage issues manually in the Linear UI; record IDs/URLs here once created. Statuses until then live in this file and HANDOFF.md.
  - Linear workspace/team: ________  |  project URL: ________  |  issue IDs MP6-S0…S9: ________
- **VS Code Codex model labels:** not needed for a ZCode run; confirm when a stage runs in VS Code.
- **Python version for `.venv`:** **3.14.5** (Homebrew `python3.14`, chosen over 3.13.5 because the full required stack resolved on it — verified at install time per 01-STAGES: faiss-cpu 1.15.1, sentence-transformers 6.1.0, torch 2.14.1 cp314 wheel, scikit-learn 1.9.1, pydantic 2.13.5). VS Code interpreter pinned via `.vscode/settings.json`.

## Stage 1 record (2026-10-07)

- **Milestone commit:** `e7a06ae3350f52d1e9b21efbd1a5709bbe0abf34` (remote SHA verified equal to local HEAD).
- **Runner/model:** ZCode session, model GLM-5.3-Flash. Sol/Terra/Luna tier table not applicable (per 03-OPERATING-RULES ZCode clause).
- **Environment:** `.venv` from `python3.14`; installed from `requirements.txt` (editable `pip install -e .` added via a minimal `pyproject.toml` so the acceptance command `.venv/bin/python -m digital_clone doctor` works with the src layout). Disk free at install: 151 GB.
- **crewai (optional, S8):** does NOT resolve on Python 3.14 — every crewai release up to 1.15.23 requires `>=3.10,<3.14`. Left commented in `requirements.txt` per the stage's "note it and continue". S8 options: a temporary 3.13.5 side-venv for the crew test, or keep `describe_crew` import-stubbed offline (decide in S8).
- **Tests:** `pytest` → 8 passed (2 config + 6 models), red-first verified (`ModuleNotFoundError` before implementation).
- **Doctor:** `.venv/bin/python -m digital_clone doctor` → `doctor: OK` (exit 0): all 14 packages present, numpy/sklearn/faiss smoke passed.

## Stage 2 record (2026-10-07)

- **Milestone commit:** `60e3325deef578a9b9b1ddf88d1c4a4be9766e61` (remote SHA verified equal to local HEAD).
- **Runner/model:** ZCode session, model GLM-5.3-Flash (ZCode clause of 03-OPERATING-RULES).
- **Tests:** 30/30 passed (22 new: features 7, email loader 5, incremental 5, style agent 5; each module red-first verified).
- **Dataset cached:** Kaggle `wcukierski/enron-email-dataset` version 2 via kagglehub at `~/.cache/kagglehub/datasets/wcukierski/enron-email-dataset/versions/2/emails.csv` (358 MB download took ~13 s; subsequent runs are cached).
- **Style profile artifact:** `data/models/style_profile_kay_mann.json` (committed) + `.joblib` (gitignored per `*.joblib` rule). Learned from 7,414 usable sent emails of `mann-k` (8,926 raw sent-folder messages; 1,512 dropped by cleaning/sender match — noted in `docs/iteration_log.md`). Top-20 sent-volume report printed pre-learning; `mann-k` confirmed as the highest-volume mailbox.
- **Visualization:** `docs/visualizations/style_feature_radar.png` (150 dpi; passed visual acceptance after removing a colliding radial-axis label).

## Stage 3 record (2026-10-07)

- **Milestone commit:** `36e4509fae759d6f04a71a345d6ceb64011bb631` (remote SHA verified equal to local HEAD). Code commits within Stage 3: `9524bca` (chunker), `1571dab` (embedders + index), `61051f8` (RAGAgent).
- **Runner/model:** ZCode session, model GLM-5.3-Flash (ZCode clause of 03-OPERATING-RULES).
- **Tests:** 43/43 passed (13 new: chunker 4, index/embedder 4, RAG agent 5; each red-first verified via `ModuleNotFoundError`). Fixture `tests/fixtures/sample_corpus.json` created (3 docs, 6 paragraphs each).
- **Knowledge base build (3 iterations — full story in `docs/iteration_log.md`):** final corpus = first 500 `computer_science` books in `open-phi/textbooks` stream order (diversity floor `min_docs=500` added to `corpus_loader.py` after builds 1–2 failed the spec's top-5 relevance spot check at 1/5 and 2/5). **210,225 chunks** (target >900), indexed in **528.6 s** (spec target <5 min — unmet, documented tension: relevance vs indexing time), **5/5 spot checks PASS** (top-1 sim 0.78–0.86, 13–62 ms ≪ 1 s). Persistence smoke: `RAGAgent.load()` restores 210,225 chunks in 8.5 s; "What is an operating system kernel?" → sim 0.83.
- **Artifacts:** `data/rag/faiss_index/index.faiss` (308 MB) and `data/rag/chunks_metadata.json` (102 MB) are **gitignored** (>.50 MB rule); rebuild: `.venv/bin/python scripts/build_knowledge_base.py`. `data/rag/build_report.json` (1.4 KB, committed) holds the measured numbers for the S6 Step-2 validation table.
- **HF dataset note:** unauthenticated streaming hits transient read timeouts; the `datasets` library's built-in retries recovered both times. Dataset schema verified (`topic`, `markdown`, `field`); `computer_science` is the dominant field (1,511 of 1,795 books).

## Notes

- The user's pasted assignment lost its HuggingFace/Kaggle hyperlink URLs in copy-paste; the dataset identities above come from the July plan's locked decisions and the assignment's own descriptions (mailbox-style Enron corpus; `open-phi/textbooks`). If Stage 2 or 3 finds a mismatch with the actual data, stop and re-confirm with the user before substituting a different source.
- Prior project `mini-project-5` used the same staged-plan pattern; its `docs/implementation/RESOURCES.md` is the format precedent.
