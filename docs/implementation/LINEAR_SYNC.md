# Linear sync queue (pending manual entry)

No Linear MCP in ZCode; the user creates the issues manually (decision 2026-10-07). Entries below are **pending synchronization** — paste them into the matching issues when they exist, and delete them from this file once recorded.

## MP6-S9 — Stage 9 (final audit, GitHub delivery, closeout)

- Status: Done (2026-10-07) — project **delivered with explicitly listed unmet criteria**; two human-only items remain (below).
- Evidence: `docs/DELIVERABLE_CHECKLIST.md` — all Final Success Criteria audited against real artifact paths: **35 met / 4 unmet (measured: confidence 0.728 < 0.80; indexing 528.6 s vs <5 min; trigger accuracy 72.7% vs >90% — OOD 1/4; whole-package coverage 82% vs 90%, core 99.3% met)**. Clean-environment smoke on a fresh clone of `af82b0b` + fresh Python 3.14.5 venv: `pip install -r requirements.txt` clean, `doctor` OK, `pytest` 81/81 (1.18 s), style profile rebuilt byte-identical (minus timestamp), KB rebuilt 210,225 chunks with identical 5/5 spot checks (wall-clock 822.8 s vs 528.6 s, documented variance), CLI verified on both branches (DELIVER final 0.88 with citations, 472 ms; FALLBACK `user_request` with booking link + 6 slots, 153 ms). Repo hygiene: 77 tracked files, none >1 MB, no credentials/datasets/caches/large binaries (content scan for key-shaped strings negative). Delivery SHA in HANDOFF.md/RESOURCES.md.
- Human acceptance: **user ran the interactive CLI themselves 2026-10-07** — worked, fallback branch triggered correctly; delivery accepted. Still outstanding: create/close the Linear issues leaving the 4 unmet criteria explicit (do not mark them met).

## MP6-S8 — Stage 8 (CrewAI mapping and reproducibility)

- Status: Done (2026-10-07)
- Evidence: `pytest` **81/81 passed** (3 new crew tests, red-first verified via `ModuleNotFoundError`); `src/digital_clone/crew.py` — `describe_crew()` offline (5 role/goal/backstory specs, July Task 15), `build_crew()` gated on `OPENAI_API_KEY` with the heavy import inside the function. crewai `<3.14` gotcha resolved with real evidence, not a stub: on a Python 3.13.5 side-venv, crewai 1.15.24 installed and `build_crew()` built a genuine 5-agent `crewai.Crew`. Full README (July Task 16 structure): architecture, setup, 5-step pipeline, results with real kept-config numbers (every number traced to `eval_results.json`/`evaluation_report.md`/`build_report.json`), design decisions incl. confidence-reweight provenance = iteration log Entry 2, deliver-vs-fallback rationale per query type, 5 known tensions. `docs/REPRODUCIBILITY.md` (new): Kaggle `emails.csv` SHA-256 `a605f0a2…8bd274`, HF `open-phi/textbooks` revision `292aaae…dacaf2` (lastModified 2023-10-08 — predates build), exact pip versions, rebuild commands, what-reproduces-exactly section. **No new tuning** (no `CloneConfig` tunable touched; iteration log's 4 entries stand). Commit SHA in HANDOFF.md. Pending sync: S0–S7 above.

## MP6-S0 — Stage 0 (access, destinations, decisions)

- Status: Done (2026-10-07)
- Evidence: private repo https://github.com/Cloisterwood/mini-project-6-digital-clone, first commit `a367683319b61962cc615f2692332fab1c866ff2` (remote SHA verified equal to local HEAD); decisions logged in RESOURCES.md.

## MP6-S1 — Stage 1 (environment, package skeleton, data models)

- Status: Done (2026-10-07)
- Evidence: Python 3.14.5 `.venv`, full required stack resolved (crewai does not — requires <3.14, noted for S8); `pytest` 8/8 passed (tests written first, red verified); `.venv/bin/python -m digital_clone doctor` → OK; commit recorded in HANDOFF.md.

## MP6-S3 — Stage 3 (knowledge base and RAGAgent)

- Status: Done (2026-10-07)
- Evidence: `pytest` 43/43 passed (13 new, red-first verified); real build: 500 docs → 210,225 chunks (>900 ✓), 5/5 top-5 relevance spot checks PASS (13–62 ms ≪ 1 s ✓); indexing 528.6 s vs <5 min target = **unmet, documented as a spec tension** (corpus expansion was the assignment's own repair for irrelevant retrieval; smaller builds measured 1/5 and 2/5 relevant). Artifacts `data/rag/faiss_index/index.faiss` (308 MB) + `chunks_metadata.json` (102 MB) gitignored per the >50 MB rule, rebuild command documented. Loader deviation (`min_docs=500`) in `docs/iteration_log.md`. Commit SHA in HANDOFF.md.

## MP6-S2 — Stage 2 (Enron data and ChatStyleAgent)

- Status: Done (2026-10-07)
- Evidence: `pytest` 30/30 passed (22 new tests, red-first verified); real build loaded 7,414 usable sent emails for `mann-k` (≥200 required; top-20 sent-volume report printed, `mann-k` #1 with 8,926 raw); 149 incremental batches; greeting/sign-off patterns learned; `data/models/style_profile_kay_mann.json` saved; `docs/visualizations/style_feature_radar.png` passed visual acceptance. Deviations logged in `docs/iteration_log.md`. Commit SHAs in HANDOFF.md/RESOURCES.md.

## MP6-S4 — Stage 4 (EvaluatorAgent and FallbackAgent)

- Status: Done (2026-10-07)
- Evidence: `pytest` 68/68 passed (25 new tests, red-first verified via `ModuleNotFoundError`); all July Task 10 tests verbatim (weighted-sum final score, hedging sensitivity, token-overlap groundedness, empty-retrieval → groundedness 0 + fallback, trigger priority, slot generation) plus Stage-4 threshold-boundary tests at 0.70/0.75/0.80 on both agents (boundary tracks `CloneConfig.fallback_threshold` — S7 tuning ready); booking link built from `config.calendar_link_template` (no hardcoded values at call sites); no tunables changed, no iteration log entry required. Commit SHAs `3a7d089`, `b1590b1` (see HANDOFF.md).

## MP6-S5 — Stage 5 (PlannerAgent, CLI, integration and e2e tests)

- Status: Done (2026-10-07)
- Evidence: `pytest` **78/78 passed** (10 new tests: July Task 11's 6 verbatim + 4 stage additions; red-first verified via `ModuleNotFoundError`). Coverage recorded: deterministic pipeline core **99.3%** (target >90% met on core), whole package **82%** — residual is entry points/real-data I/O accepted via S1–S3 real runs (doctor, `__main__`, HF corpus loader, Enron CSV path, SentenceEmbedder lazy paths); tension recorded, not hidden. Real-artifact CLI smoke: `"What is TCP/IP?"` → final 0.84 DELIVER, 509 ms; `"Can we schedule a call?"` → FALLBACK `user_request`, config-template calendar link, 6 slots, 242 ms — both ≪ 1 s query-latency target. Simulated component failure degrades to `system_error`; decision log = one JSONL line per query. Commit `c92741b` (see HANDOFF.md).

## MP6-S6 — Stage 6 (real-artifact integration and baseline evaluation)

- Status: Done (2026-10-07)
- Evidence: real pipeline wired (`build_planner(CloneConfig())` loads the S2 profile (7,414 emails) + S3 FAISS index (210,225 chunks) with SentenceEmbedder); CLI smoke re-verified on real artifacts (TCP/IP → 0.84 DELIVER 599 ms; booking → `user_request` FALLBACK 147 ms). `scripts/run_evaluation.py` (July Task 13) run for real: 20/20 queries, 0 crashes (reliability 100%); latency 41 ms mean / 56 ms p95; in-domain final 0.845; style 0.999; groundedness 0.648. **Gaps recorded honestly (S7 input)**: fallback rate 50% > 40% target; confidence 0.572 < 0.80 (spec-formula cap, tension #1); OOD wrong-delivery "Explain dark matter physics" at 0.81; indexing 528.6 s (S3 tension). Artifacts: `data/evaluations/eval_results.json` + `decision_log.jsonl` (20 lines) + `docs/evaluation_report.md` (Step 1–5 tables) + `docs/iteration_log.md` Entry 1 — Baseline. Commit `f077bb4` (remote SHA verified equal to local HEAD). Pending sync: S0–S5 above.

## MP6-S7 — Stage 7 (tuning iterations and required visualizations)

- Status: Done (2026-10-07)
- Evidence: `pytest` **78/78 passed** (confidence-formula weights made `CloneConfig`-driven, spec defaults preserved until tuned; kept config verified by full suite). Experiment 2 — confidence reweight `0.6·relevance + 0.4·completeness − penalty`: confidence 0.572 → **0.728**, fallback rate 50% → **40%** (in band), in-domain final 0.845 → 0.881 — **kept** (iteration log Entry 2, `CloneConfig` defaults updated to 0.6/0.4). Experiment 3 — threshold 0.75 → 0.70: fallback rate 30% but **all 4 out-of-domain queries delivered** (World Series 0.719) — **rejected**, threshold reverted (Entry 3). Final default-config rerun reproduced Entry 2's scores exactly (deterministic; `data/evaluations/eval_results.json`, decision log 20 lines). `scripts/make_visualizations.py` → 6 PNGs in `docs/visualizations/` (radar, style/groundedness distributions, final-score breakdown vs 0.75 line, fallback rate by type vs 30–40% band, latency vs 1 s line); visual acceptance: 4/6 first pass, 2 legend-overlap repairs, re-judged. Remaining gaps recorded honestly: confidence 0.728 < 0.80 (both prescribed knobs exhausted), delivered-OOD 3/4, indexing 528.6 s (S3 tension). Commit SHA in HANDOFF.md. Pending sync: S0–S6 above.
