# Linear sync queue (pending manual entry)

No Linear MCP in ZCode; the user creates the issues manually (decision 2026-10-07). Entries below are **pending synchronization** — paste them into the matching issues when they exist, and delete them from this file once recorded.

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
