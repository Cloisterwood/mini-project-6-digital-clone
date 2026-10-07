# Build stages

Every stage ends with the checkpoint procedure in `03-OPERATING-RULES.md`, then STOP. An earlier 75% context stop leaves that stage In Progress; resume it before advancing. Each stage is one Linear issue (local planning keys MP6-S0…MP6-S9; record real Linear IDs in the handoff). "July Tasks" refer to `docs/superpowers/plans/2026-07-04-enron-digital-clone.md`, the implementation reference whose code sketches and tests are used as-is unless this file says otherwise.

## Stage 0 — access, destinations, and decisions

Model: Sol. Dependencies: none.

- Inspect existing files. Preserve the July plan and this plan's docs; nothing else exists yet.
- Confirm and record in RESOURCES.md: GitHub destination (private repo under account `Cloisterwood`; gh CLI is authenticated on the Mac — propose a name such as `mini-project-6-digital-clone` and get user confirmation before creating), Linear team/project, and which Codex model labels are actually available in VS Code (user reports "Codex Sol 5.1"; MP5 records "Sol 6.1" — record the real picker labels for Sol/Terra/Luna; the human changes the picker if the agent cannot).
- Connect Linear in VS Code through its supported MCP integration; user handles browser OAuth. Create/reuse a project named `Mini-project 6 — Enron digital clone`; create issues MP6-S0 through MP6-S9 using the titles here, each with objective, dependencies, owned files, acceptance checks, and assistant tier. Record real IDs/URLs in the handoff.
- Initialize a standalone Git repository in this folder, add `.gitignore` before staging (`.venv/`, `__pycache__/`, `data/raw/`, `data/emails/`, `*.joblib`, `.DS_Store`, `.env*` except a value-free example), commit the plan docs, publish to the confirmed repo, and verify the remote SHA.
- Freeze the system contract (02); flag grading ambiguities for instructor clarification when available and proceed with the documented default interpretation otherwise.

Acceptance: real Linear issue links and a verified GitHub plan commit recorded in RESOURCES.md/HANDOFF.md; dataset acquisition path known. If auth/destination is missing, checkpoint as Blocked and list the exact human action. No fabricated integration success.

**STOP S0.**

## Stage 1 — environment, package skeleton, and data models

Model: Sol; Luna may handle straightforward documentation. Dependencies: S0. July Tasks 1–2.

- Choose a Python 3.10+ interpreter whose dependency resolution succeeds (system offers Homebrew 3.14 and 3.13.5; faiss-cpu/sentence-transformers wheel availability decides — verify at install time, not by assumption). Create `.venv`, set the VS Code interpreter explicitly, record the version in RESOURCES.md.
- Create `requirements.txt` (pydantic, numpy, scikit-learn, faiss-cpu, sentence-transformers, langchain-text-splitters, datasets, kagglehub, pandas, matplotlib, seaborn, joblib, pytest, pytest-cov; `crewai` optional — if it fails to resolve, note it and continue, it is only needed for S8), `pytest.ini`, `README.md` stub, and `src/digital_clone/` with `style/`, `rag/`, `agents/` packages plus `tests/`.
- Implement `CloneConfig` (every tunable: weights 0.4/0.4/0.2, threshold 0.75, alpha 0.3, batch 50, chunk 500/50, top_k 5, min_chunks 900, employee fields, paths) and the Pydantic models (`EmailMessage`, `StyleProfile`, `KnowledgeChunk`, `RetrievedChunk`, `EvaluationResult`, `FallbackResponse`, `CloneResponse`) exactly as in July Tasks 1–2, tests first.
- Implement `python -m digital_clone doctor`: interpreter and package versions, import checks, disk space, and fixture-free smoke of numpy/sklearn/faiss imports. (No GPU detection needed — everything runs CPU.)

Acceptance: `.venv/bin/python -m digital_clone doctor` passes; `pytest` runs the config and models tests green; chosen Python version recorded. Record the exact environment, not a claim that all tests pass when only some exist.

**STOP S1.**

## Stage 2 — Enron data and ChatStyleAgent (style learning)

Model: Sol. Dependencies: S1. July Tasks 3–6 plus the style half of Task 12.

- Implement the 13 numeric style features + metadata extraction (`features.py`), the Enron loader (`email_loader.py`: parse RFC-822, strip forwarded chains, sent-folder filter, fixture loading), the incremental learner (`incremental.py`: StandardScaler + PCA on first batch, EMA updates `profile = (1-α)·profile + α·batch`, history, joblib persistence), and `ChatStyleAgent` (`learn`, `style_score`, `apply_style`, `save`/`load`) — tests first, offline with fixtures, per the July code.
- Write `scripts/build_style_profile.py` (July Task 12 Step 1): download the Kaggle corpus via `kagglehub.dataset_download("wcukierski/enron-email-dataset")` (~358 MB, cached), filter `mann-k` sent folders + sender match, assert ≥200 usable emails.
- Before learning, print a top-20 sent-volume report across mailboxes (counts only) so the employee choice is verifiable; if `mann-k` yields <200 after cleaning, switch to the documented `dasovich-j` fallback and record the change. Report per-batch profile deltas (style evolution) from `learner.history`.
- Run the script; save `data/models/style_profile_{employee}.json` (+ joblib). Produce `docs/visualizations/style_feature_radar.png` (spec chart 1) from the profile — normalized features, labeled, colorblind-friendly.

Acceptance: all July feature/loader/learner/agent tests pass offline; the real build prints the loaded-email count (≥200), batch history length >1, and learned greeting/sign-off patterns; radar PNG exists and was visually inspected. Any deviation (employee switch, dropped emails) goes in the iteration log as a note.

**STOP S2.**

## Stage 3 — knowledge base and RAGAgent

Model: Sol; Terra acceptable for the build script once tests are green. Dependencies: S1. July Tasks 7–9 plus the RAG half of Task 12.

- Implement `chunker.py` (RecursiveCharacterTextSplitter, 500/50, global sequential `chunk_index`, metadata preserved), `embedder.py` (`HashEmbedder` deterministic offline + `SentenceEmbedder` all-MiniLM-L6-v2, same interface), `index.py` (FAISS `IndexFlatIP` with L2 normalization on add and search, save/load), `corpus_loader.py` (streaming `open-phi/textbooks`, field filter "computer", stop at ≥900-chunk estimate with 20% headroom), and `RAGAgent` (`build`, `retrieve` with clipped similarities, `generate` with `"[n] topic (chunk idx)"` citations, `save`/`load`) — tests first with fixtures, per the July code.
- Write and run `scripts/build_knowledge_base.py` (July Task 12 Step 2): record selected docs, chunk count (>900), indexing time (<5 min target), and spot-check retrieval for 5 queries (relevance in top-5, <1s per query) — the spec's Step 2 validation table.
- If spot checks return irrelevant chunks: adjust chunk size (300–800) or overlap, or refocus the field filter; document in the iteration log before re-indexing.

Acceptance: July chunker/index/RAG tests pass offline with `HashEmbedder`; the real build logs chunk count, indexing seconds, and the 5-query spot-check table; artifacts saved to `data/rag/faiss_index/index.faiss` + `chunks_metadata.json` (gitignore the index binary if >50 MB, note the rebuild command).

**STOP S3.**

## Stage 4 — EvaluatorAgent and FallbackAgent

Model: Sol for scoring design; Terra for bounded implementation once the contract is fixed. Dependencies: S1 (tests use fixtures, not S2/S3 artifacts). July Task 10.

- Implement `EvaluatorAgent`: groundedness `0.5·mean_similarity + 0.5·token_overlap`, confidence per the spec pseudocode `0.5·relevance + 0.3·completeness − hedging_penalty` (clipped), final score `w_style·style + w_grounded·groundedness + w_conf·confidence` read from `CloneConfig`, decision `deliver` iff `final ≥ threshold`. Style score arrives as a callable injected from ChatStyleAgent.
- Implement `FallbackAgent.should_fallback` with the exact priority `system_error → user_request → low_confidence → high_uncertainty → None`, and `build_response` producing context summary (query + reason + score breakdown), simulated calendar link `https://calendly.com/{employee_name}/30min`, and 6 slots (next 3 weekdays, 10:00/14:00).
- Tests per the July code, plus threshold-boundary tests at 0.70/0.75/0.80 to prepare S7 tuning. All scores clipped to [0,1]; empty retrieval forces groundedness 0 and fallback.

Acceptance: July evaluator/fallback tests pass, including hedging sensitivity, token-overlap groundedness, trigger priority, and slot generation. No config values hardcoded at call sites.

**STOP S4.**

## Stage 5 — PlannerAgent, CLI, integration and e2e tests

Model: Sol. Dependencies: S2–S4. July Task 11.

- Implement `PlannerAgent.process(query)`: retrieve → generate → apply_style → evaluate → deliver or fallback, with `time.perf_counter` latency, JSONL decision log, and any sub-agent exception converted to a graceful `system_error` fallback — never a crash. Implement `build_planner(config)` factory loading persisted artifacts. Implement the CLI (`--query` one-shot or interactive REPL) with score rendering.
- Integration tests (July `test_planner.py`): in-domain response, booking request forced fallback, simulated component failure degrades gracefully, decision log written. E2E tests (July `test_e2e.py`): 5 query types complete under 1s with fixtures.
- Run the full suite: ≥23 unit tests required (July suite is ~43), all green. Measure coverage of `src/digital_clone` core (`pytest --cov`) — target >90%, record actual.

Acceptance: full pytest suite green offline; coverage number recorded; CLI renders scores and both branches (deliver/fallback) against fixtures. This stage proves the architecture; real artifacts arrive in S6.

**STOP S5.**

## Stage 6 — real-artifact integration and baseline evaluation

Model: Sol. Dependencies: S2, S3, S5.

- Wire the real pipeline end-to-end: `build_planner(CloneConfig())` loads the S2 style profile and S3 FAISS index with `SentenceEmbedder`; smoke-test the CLI on real artifacts (`What is TCP/IP?` and `Can we schedule a call?`) and record observed latencies after model load.
- Implement and run `scripts/run_evaluation.py` (July Task 13): the fixed 20-query set (5 in-domain factual, 4 how-to, 4 out-of-domain, 3 ambiguous, 4 booking requests), writing `data/evaluations/eval_results.json` + `data/evaluations/decision_log.jsonl` and generating `docs/evaluation_report.md` with the spec's Step 1–5 validation tables (features, per-query scores, fallback trigger table, system summary vs targets).
- Create `docs/iteration_log.md` and record **Entry 1 — Baseline** with the actual summary numbers (fallback rate, mean scores, latency mean/p95, reliability, crashes). Compare honestly against every target in 02 — do not tune yet.

Acceptance: baseline report generated from real artifacts with measured numbers; per-query table filled; gaps vs targets listed explicitly (they are S7's input). If a target is already missed structurally (e.g., a bug, not tuning), fix the bug here and note it — tuning experiments wait for S7.

**STOP S6.**

## Stage 7 — tuning iterations and required visualizations

Model: Sol for diagnosis; Terra for plotting. Dependencies: S6.

- Run ≥2 tuning experiments against the baseline, each = change config → rerun `run_evaluation.py` → append an iteration log entry (change, reason, before, after, delta, keep) in the exact 02 format. Expected knobs (from the July plan, applied only if the baseline shows the corresponding gap): confidence reweight `0.6·relevance + 0.4·completeness − penalty` if mean confidence ≤0.80; threshold 0.70 or 0.78–0.80 if fallback rate is outside 30–40%; chunk size 800 or top_k raise if groundedness <0.60; folder filtering if style <0.90.
- Keep changes traceable: the last "Keep? Yes" entry must match `CloneConfig` defaults at delivery. Never tune on the evaluation set more than the logged experiments allow — the evaluation set is the only benchmark this project has, so logged-and-kept changes only, no silent rerolling.
- Implement and run `scripts/make_visualizations.py` (July Task 14): the 6 required PNGs (style radar regenerated from the final profile, style score distribution, groundedness distribution, final-score breakdown with 0.75 line, fallback rate by query type with 30–40% band, latency distribution with 1s line) in `docs/visualizations/`. Quality bar: descriptive titles, labeled axes, grid lines, colorblind-friendly palettes, fonts ≥10pt, 150 dpi.
- Regenerate the final report with the kept configuration; visually inspect every PNG (the human should look at them too).

Acceptance: ≥3 iteration log entries total (baseline + ≥2 experiments), final config traceable; 6 PNGs present and legible; final `eval_results.json`/report reflect the kept config.

**STOP S7.**

## Stage 8 — CrewAI mapping and reproducibility

Model: Terra; Sol for the audit paragraphs. Dependencies: S7. July Tasks 15–16 (docs half).

- Implement `crew.py` per July Task 15: `describe_crew()` returning the 5 role/goal/backstory specs, `build_crew()` only active with `OPENAI_API_KEY` set. Test `describe_crew` offline. This satisfies the spec's CrewAI stack item while the graded execution path stays deterministic — README explains why (latency target).
- Write the full README: architecture, setup, full pipeline commands, tests, **results with real numbers from the final report**, design decisions (template generation, raw-feature cosine scoring, confidence reweight provenance, CrewAI mapping), deliver vs fallback rationale per query type, known deviations.
- Write `docs/REPRODUCIBILITY.md`: dataset sources and hashes (Kaggle corpus file hash, HF dataset revision if pinnable), artifact rebuild commands, interpreter version, dependency list.

Acceptance: crew test passes; README contains no target numbers without a measured source; a reader can reproduce the pipeline from README alone. No new tuning in this stage.

**STOP S8.**

## Stage 9 — final audit, GitHub delivery, and closeout

Model: Sol for the final audit; Luna for small editorial fixes. Dependencies: S8.

- Build `docs/DELIVERABLE_CHECKLIST.md`: every checkbox in the spec's Final Success Criteria (Phases 1–5, visualizations, iteration logs, testing/docs) audited against a real artifact path. Do not mark unmet performance targets complete — list them as unmet with measured values.
- Clean-environment smoke: fresh venv from `requirements.txt`, run the pipeline per README (build scripts, tests, one CLI query of each branch), confirm it works without undocumented steps.
- Final review/stage of named files, commit, push, verify remote SHA equals local HEAD; record the URL + SHA in RESOURCES.md. Confirm no credentials, datasets, caches, or oversized binaries entered the repository.
- Update Linear: complete checks, evidence links, close only completed issues; leave unmet criteria explicit. Final handoff update; end with `STOP S9 — project delivered` or `— delivered with explicitly listed unmet criteria`.

Acceptance: another person can clone the repo, follow README, and verify the submitted commit. The user has run the interactive CLI themselves at least once.

**STOP S9 — project delivered, or delivered with explicitly listed unmet criteria.**
