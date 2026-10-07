# Handoff — current state

**Planning date:** October 6, 2026 (plan created by ZCode from the user's pasted assignment).
**Status:** **Stage 6 complete** (2026-10-07, ZCode, model GLM-5.3-Flash; Stages 0–5 completed 2026-10-07 same runner). Next action: **Stage 7**.

## Next action

Run Stage 7 (tuning iterations + required visualizations — July Task 14) from `01-STAGES.md`. Dependency S6 complete. Scope: ≥2 tuning experiments against the measured baseline, each = change config → rerun `scripts/run_evaluation.py` → append an iteration log entry in the exact 02 format (change, reason, before, after, delta, keep); then `scripts/make_visualizations.py` producing the 6 required PNGs in `docs/visualizations/`; regenerate the final report with the kept configuration. **The baseline's measured gaps are S7's input** (`docs/evaluation_report.md` "Gaps" section): fallback rate 50% > 40% target (knob: threshold 0.70 — but note the recorded tension that lowering it delivers more out-of-domain queries, e.g. "Explain dark matter physics" already delivered at 0.81); confidence 0.572 < 0.80 (spec-formula cap, tension #1 — knob: reweight `0.6·relevance + 0.4·completeness − penalty`); style 0.999 and groundedness 0.648 already meet targets (no knob needed); indexing 528.6 s is an offline-cost tension, not query-tunable. Other knobs (chunk size 800, top_k raise, folder filtering) apply only if their corresponding gap shows. Never tune on the evaluation set beyond logged experiments; the last "Keep? Yes" entry must match final `CloneConfig` defaults. Visual quality bar: descriptive titles, labeled axes, grid, colorblind-safe, ≥10 pt, 150 dpi; every PNG passes visual inspection. The user's outstanding Stage 0 follow-through (still open): create the ten Linear issues, paste IDs/URLs into RESOURCES.md, mark MP6-S0…S6 Done using `docs/implementation/LINEAR_SYNC.md`. Stage 9 human task: run the interactive CLI yourself (`python -m digital_clone.cli`).

## Stage 6 record (2026-10-07)

- **Runner/model:** ZCode session, model GLM-5.3-Flash (ZCode clause of 03-OPERATING-RULES).
- **Commit:** `f077bb4` — pushed to `origin/main`, remote SHA verified equal to local HEAD. Files: `scripts/run_evaluation.py` (new), `docs/evaluation_report.md` (generated), `docs/iteration_log.md` (Entry 1), `data/evaluations/eval_results.json` + `decision_log.jsonl` (20 lines, one per query).
- **Real-pipeline wiring verified:** `build_planner(CloneConfig())` loads the S2 profile (7,414 emails) + S3 FAISS index (210,225 chunks, 308 MB) with `SentenceEmbedder` (~10 s load). CLI smoke re-run: "What is TCP/IP?" → style 1.00, final 0.84 → DELIVER, 599 ms; "Can we schedule a call?" → final 0.74 → FALLBACK `user_request`, 147 ms. Smoke decision log deleted before the evaluation run (S6's eval owns that path).
- **Harness (July Task 13, no tests per S2/S3 script precedent — validated by the real run):** `TEST_QUERIES` 20 verbatim; per-query records keep July's field names verbatim (Task 14 reads them) with two extensions for the Step 4 table (`fallback_context_summary`, `fallback_calendar_link`); summary adds `mean_final_in_domain` (the 02 target is in-domain), `fallback_by_query_type`/`fallback_by_trigger`, and micro-benchmarks: eval speed = mean of 50 `evaluator.evaluate()` calls on a real in-domain sample, retrieval time re-measured on the 5 factual queries. Report generator writes the assignment's Step 1–5 tables from `data/rag/build_report.json` (S3 evidence, as planned in S3) plus a targets-vs-measured table and a computed gaps list; it also detects **delivered out-of-domain queries** (assignment Step 4 repair note).
- **Baseline measured (default `CloneConfig`, no tuning):** reliability 100% (0 crashes / 20); latency **41 ms mean, 56 ms p95** (warm run; first run 89/432 ms — both ≪ 1 s); fallback rate **50%** (6 `low_confidence` + 4 `user_request`; by type: in-domain 0/9, OOD 3/4, ambiguous 3/3, booking 4/4); style 0.999 ✓, groundedness 0.648 ✓, confidence **0.572 ✗** (spec-formula cap, tension #1), final in-domain **0.845 ✓**; eval speed 0.14 ms ✓; retrieval 13.1 ms ✓; indexing 528.6 s ✗ (S3 tension carried).
- **Gaps → S7 (recorded in report + iteration log):** fallback rate 50% > 40% (threshold knob; tension with OOD delivery — "Explain dark matter physics" was **delivered** at 0.81 because MiniLM grounds it at 0.70 with high token overlap, so lowering the threshold worsens wrong-deliveries while raising it pushes fallback rate further up); confidence 0.572 < 0.80 (logged reweight experiment). Trigger priority untouched per contract.
- **No deviations** from July Task 13 beyond the documented extensions; no `CloneConfig` tunable changed.

## Stage 5 record (2026-10-07)

- **Runner/model:** ZCode session, model GLM-5.3-Flash (ZCode clause of 03-OPERATING-RULES).
- **Code commit:** `c92741b` — tests written first (red verified via `ModuleNotFoundError: No module named 'digital_clone.agents.planner_agent'`), then implementation.
- **Code:** `agents/planner_agent.py` — `PlannerAgent.process(query)` orchestrates retrieve → generate → apply_style → evaluate; `time.perf_counter` latency; JSONL decision log via `CloneResponse.model_dump_json()` append; any sub-agent exception is captured and routed to `should_fallback(..., error=...)` → graceful `system_error` fallback, never a crash. `build_planner(config, embedder=None)` factory loads the persisted style profile + FAISS index/metadata and wires all five agents with `decision_log_path = config.eval_dir / "decision_log.jsonl"` (SentenceEmbedder default, injectable for offline use). `cli.py` — `--query` one-shot or interactive REPL (quit/exit/EOF), renders style/grounded/confidence/final scores + decision, response or fallback (reason, context summary, calendar link, 6 slots) and per-query latency.
- **Tests:** July Task 11's 6 tests verbatim (in-domain response <1s, booking → `user_request` with calendar link, simulated component failure → `system_error`, decision log one line per query, 5 query types complete <1s, booking/out-of-domain fall back) **plus 4 Stage-5 additions** (factory artifact round-trip incl. decision-log write; CLI one-shot deliver-branch rendering; CLI one-shot fallback-branch rendering; REPL query-then-EOF). CLI tests run fully offline: fixture-built artifacts in `tmp_path`, `monkeypatch.chdir` so `CloneConfig()`'s relative data dir resolves, and `digital_clone.rag.embedder.SentenceEmbedder` patched to `HashEmbedder(dim=64)` (the fixture index's backend). Full suite: **78/78 passed** (68 prior + 6 July + 4 additions) in ~1.5 s.
- **Coverage (`pytest --cov=digital_clone --cov-report=term-missing`), recorded honestly:** whole package **82%** (602 stmts, 107 miss) — below the >90% target if read as whole-package; **deterministic pipeline core 99.3%** (452 stmts, 3 trivial misses: `style_agent.py:48` profile-None branch, `cli.py:47,52` KeyboardInterrupt + `__main__` guard) — target met on the core reading. The whole-package residual is entry points and real-data I/O, each accepted via earlier real runs: `doctor.py` 0% (S1 ran it for real), `__main__.py` 0% (wrapper), `rag/corpus_loader.py` 0% (HF streaming path, S3 real build), `style/email_loader.py` 68% (real-CSV parsing, S2 real build), `rag/embedder.py` 80% (SentenceEmbedder lazy paths, real builds). Recorded as a tension, not hidden; no test contortions added to chase the aggregate.
- **Real-artifact CLI smoke (optional stage item, artifacts from S2/S3):** `python -m digital_clone.cli --query "What is TCP/IP?"` → final 0.84 → DELIVER, styled reply with 3 citations, **509 ms** query latency (≈10.5 s total incl. MiniLM + 308 MB index load). `--query "Can we schedule a call?"` → final 0.74 → FALLBACK with trigger **`user_request`** (correctly prioritized over the would-be `low_confidence`), calendar link `https://calendly.com/kay_mann/30min` from the config template, 6 slots (Oct 8/9/12 — weekend skipped), **242 ms**. Smoke-written `data/evaluations/decision_log.jsonl` deleted afterward; S6's evaluation run owns that path.
- **Boundary note:** with the 12-email fixture profile, the TCP query lands at final exactly 0.75 → deliver (`≥` semantics from S4); deterministic arithmetic, so the July in-domain test's "delivered or fallback both acceptable" branch is stable. Real-profile smoke delivers at 0.84.
- **No deviations** from July Task 11; the 4 extra tests are stage additions (S4 precedent), not replacements. No tunables changed; no iteration log entry needed.

## Stage 4 record (2026-10-07)

- **Runner/model:** ZCode session, model GLM-5.3-Flash (ZCode clause of 03-OPERATING-RULES).
- **Code commits:** `3a7d089` (EvaluatorAgent + tests), `b1590b1` (FallbackAgent + tests). Tests written first each time; red verified via `ModuleNotFoundError` before each implementation.
- **Code:** `agents/evaluator_agent.py` — groundedness `0.5·mean_similarity + 0.5·token_overlap` (clipped), confidence per spec pseudocode `0.5·relevance + 0.3·completeness − min(0.15·hedge_count, 0.5)` (clipped) returning `(score, hedge_count)`, final score from `CloneConfig` weights, decision `deliver` iff `final ≥ fallback_threshold`, style injected as a callable. `agents/fallback_agent.py` — `should_fallback` priority exactly `system_error → user_request → low_confidence → high_uncertainty → None`, `build_response` with context summary, calendar link from `config.calendar_link_template.format(employee_name=…)` (S1 deviation honored — nothing hardcoded at call sites), 6 slots = next 3 weekdays × (10:00, 14:00).
- **Tests:** 25 new (12 evaluator + 13 fallback), all July Task 10 tests verbatim plus Stage-4 additions: threshold-boundary tests at **0.70/0.75/0.80** on both agents (decision boundary tracks `CloneConfig.fallback_threshold`, exact-boundary semantics `deliver iff ≥`), trigger-priority ordering, config-template calendar link, no-evaluation fallback summary, weekday/time slot generation (Wed 2026-10-07 → Thu 8, Fri 9, Mon 12), confidence clipped to 0 under hedge flood. Full suite: **68/68 passed** (43 prior + 25 new).
- **No deviations** from July Task 10 beyond the already-documented `calendar_link_template` rule (stage requirement, not a deviation). No iteration log entry needed — no tunables changed; defaults untouched.

## Stage 3 record (2026-10-07)

- **Runner/model:** ZCode session, model GLM-5.3-Flash (ZCode clause of 03-OPERATING-RULES).
- **Milestone commit:** `36e4509fae759d6f04a71a345d6ceb64011bb631` — pushed to `origin/main`, remote SHA verified equal to local HEAD. Code commits within Stage 3: `9524bca` (chunker), `1571dab` (embedders + index), `61051f8` (RAGAgent).
- **Code (tests first, red verified via `ModuleNotFoundError` before each implementation):** `rag/chunker.py` (4 tests), `rag/embedder.py` + `rag/index.py` (4 tests), `rag/corpus_loader.py` + `agents/rag_agent.py` (5 tests), fixture `tests/fixtures/sample_corpus.json`. Full suite: **43/43 passed** (30 prior + 13 new).
- **Script:** `scripts/build_knowledge_base.py` — July Task 12 Step 2 extended with the spec's full Step-2 validation (5 spot-check queries with relevance-in-top-5 and per-query latency) and per-phase timings; writes `data/rag/build_report.json`.
- **Real build ran 3×** (story + evidence in `docs/iteration_log.md`): build 1 (July loader stop rule) selected **1 textbook** → 1,476 chunks, spot checks 1/5 relevant; build 2 (`min_docs=8` repair) → 11,767 chunks, 2/5 relevant; a full-dataset keyword scan located the missing topics deeper in the fixed stream order, so build 3 used **`min_docs=500`** → 500 docs, **210,225 chunks** (>900 ✓), **5/5 spot checks PASS** (top-1 sim 0.78–0.86, **13–62 ms** ≪ 1 s), persistence smoke reload in 8.5 s with in-domain queries hitting sim 0.82–0.85.
- **Target miss (recorded, not hidden):** indexing **528.6 s vs <5 min target** — the cost of the corpus expansion the assignment itself prescribes for irrelevant retrieval; documented as a new spec tension (relevance vs indexing time). Query-time latency (the runtime target) is 13–62 ms.
- **Artifacts:** `data/rag/faiss_index/index.faiss` (308 MB) and `data/rag/chunks_metadata.json` (102 MB) **gitignored** (>50 MB rule; rebuild: `.venv/bin/python scripts/build_knowledge_base.py`); `data/rag/build_report.json` committed for the S6 validation table.
- **Deviations:** `corpus_loader.py` stop-condition diversity floor (logged); Big-O spot-check keyword `big-o`→`complexity` (logged); HF streaming hit transient read timeouts twice — `datasets` built-in retries recovered, no data affected.

## Stage 2 record (2026-10-07)

- **Runner/model:** ZCode session, model GLM-5.3-Flash (Sol/Terra/Luna table not applicable).
- **Milestone commit:** `60e3325deef578a9b9b1ddf88d1c4a4be9766e61` — pushed to `origin/main`, remote SHA verified equal to local HEAD. Code commits within Stage 2: `33a0ebe` (features), `f4368d8` (loader), `6c6d080` (learner), `037abec` (style agent).
- **Code (tests first, red verified via `ModuleNotFoundError` before each implementation):** `style/features.py` (7 tests), `style/email_loader.py` + 12-email fixture + `conftest.py` (5 tests), `style/incremental.py` (5 tests), `agents/style_agent.py` (5 tests). Full suite: **30/30 passed** (8 prior + 22 new).
- **Scripts:** `scripts/build_style_profile.py` (July Task 12 Step 1 + Stage 2 additions: top-20 sent-volume report before learning, documented dasovich-j fallback if <200, per-batch delta report) and `scripts/plot_style_radar.py` (spec chart 1).
- **Real build evidence:** Kaggle corpus downloaded via kagglehub (358 MB, cached at `~/.cache/kagglehub/.../versions/2/emails.csv`). Top-20 report printed; `mann-k` is #1 with 8,926 raw sent-folder messages. **7,414 usable sent emails** loaded for `kay.mann@enron.com` (≥200 required — no fallback switch). **149 batches** processed (history length >1 ✓); learned greeting "hi" (12.5%) and sign-off "thanks" (25.3%). Profile saved to `data/models/style_profile_kay_mann.json` (+ joblib, gitignored).
- **Radar PNG:** `docs/visualizations/style_feature_radar.png` regenerated after a visual-judge repair (removed a radial-axis label that collided with two feature labels); final render **passed** visual acceptance (title, 13 legible labels, grid, colorblind-safe color, 150 dpi).
- **Deviations:** recorded in `docs/iteration_log.md` (dropped-emails note; batches 71–80 EMA delta spike kept as a real corpus property). No employee switch; no config changes.

## Stage 1 record (2026-10-07)

- **Milestone commit:** `e7a06ae3350f52d1e9b21efbd1a5709bbe0abf34` — pushed to `origin/main`, remote SHA verified equal to local HEAD.

- Python **3.14.5** `.venv`; full required stack resolved on it (faiss-cpu 1.15.1, sentence-transformers 6.1.0, scikit-learn 1.9.1, pydantic 2.13.5). Full details in RESOURCES.md.
- `pytest`: **8/8 passed** (2 config + 6 models), written red-first per the July plan.
- `.venv/bin/python -m digital_clone doctor`: **OK** (versions, import smoke numpy/sklearn/faiss, disk 151 GB free).
- `crewai` does not resolve on 3.14 (all releases require <3.14) — commented in `requirements.txt`; S8 decision noted in RESOURCES.md.
- Deviation from July Task 1, documented: `CloneConfig` gained `calendar_link_template` (02-SYSTEM-CONTRACT lists the booking link as a CloneConfig default and forbids hardcoding at call sites); `pyproject.toml` added for the editable install so the doctor acceptance command works from the repo root; `.vscode/settings.json` pins the interpreter.

## Decisions already made (do not re-litigate)

1. No runtime LLM — template-based response generation (user, 2026-10-06).
2. Simulated calendar booking — no external calendar API (user, 2026-10-06).
3. Default employee Kay Mann (`mann-k`), configurable, `dasovich-j` documented fallback; Stage 2 verifies ≥200 sent emails and prints a top-20 report.
4. Plan docs only were created in this session; repo/env/Linear bootstrap happens in Stage 0 in VS Code.
5. The July plan (`docs/superpowers/plans/2026-07-04-enron-digital-clone.md`) is the technical reference; its execution instructions are superseded by `01-STAGES.md`.

## Unresolved setup details (Stage 0's job)

- [x] GitHub repo created (private): https://github.com/Cloisterwood/mini-project-6-digital-clone — plan pushed, commit `a3676833`, remote SHA verified (2026-10-07).
- [x] Python interpreter for `.venv` chosen in S1 after dependency resolution: 3.14.5 (see RESOURCES.md).
- [ ] Linear project + issues MP6-S0…S9 created; real IDs/URLs recorded. User chose manual creation (2026-10-07); pending their paste-back (evidence ready in docs/implementation/LINEAR_SYNC.md).
- [ ] Actual VS Code Codex model labels recorded (only needed when a stage runs in VS Code).

## Environment facts (verified 2026-10-06 on this Mac)

- gh CLI authenticated as `Cloisterwood` (repo scope).
- Apple M2, 24 GB RAM; no GPU needed for this project.
- `git 2.53.0`; `uv` not on PATH (plain `python3 -m venv` is fine; install uv only if preferred).
- No Linear CLI on PATH; Linear access goes through the VS Code MCP integration.

## Human-only tasks (blockers if not done)

1. **After S0 (now):** create the ten Linear issues from the paste list; mark MP6-S0 Done with repo URL + commit `a3676833` as evidence; paste IDs/URLs back.
2. **Stage 2:** none expected — employee decision pre-made; only if `mann-k` yields <200 usable emails does the fallback switch need your awareness (it is logged, not blocked).
3. **Stage 9:** run the interactive CLI yourself and accept delivery.
