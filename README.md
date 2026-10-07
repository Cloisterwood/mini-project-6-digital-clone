# Enron Digital Clone (mini-project 6)

A deterministic five-agent "digital clone" of an Enron employee (default: Kay Mann) that answers questions in their email style, grounded in a computer-science textbook knowledge base, with weighted quality evaluation and calendar-booking fallback. **No runtime LLM** — the graded pipeline is fully deterministic and offline; query latency is milliseconds, not API round-trips.

**Status:** **Delivered 2026-10-07** — all nine stages complete. Final Success Criteria audit: [docs/DELIVERABLE_CHECKLIST.md](docs/DELIVERABLE_CHECKLIST.md) (34 met / 4 unmet, each unmet item stated with its measured value). Delivery commit SHA recorded in [docs/implementation/RESOURCES.md](docs/implementation/RESOURCES.md). Stage plan: [docs/implementation/01-STAGES.md](docs/implementation/01-STAGES.md); system contract: [docs/implementation/02-SYSTEM-CONTRACT.md](docs/implementation/02-SYSTEM-CONTRACT.md); dataset hashes + rebuild details: [docs/REPRODUCIBILITY.md](docs/REPRODUCIBILITY.md).

## Architecture

```
                     query
                       │
                       ▼
               ┌──────────────┐   retrieve top-k   ┌───────────────┐
               │ PlannerAgent │───────────────────▶│    RAGAgent   │──▶ FAISS index
               │ (cli.py,     │                    │ (rag_agent.py)│    (210,225 chunks,
               │ planner_     │◀───────────────────│               │     MiniLM vectors)
               │  agent.py)   │   cited answer     └───────────────┘
               │              │
               │              │   apply style      ┌───────────────┐
               │              │───────────────────▶│ ChatStyleAgent│──▶ style profile
               │              │◀───────────────────│ (style_agent. │    (7,414 sent emails,
               │              │   styled response  │  py)          │     13 features, EMA)
               │              │
               │              │   evaluate         ┌───────────────┐
               │              │───────────────────▶│ EvaluatorAgent│
               │              │◀─── final score ───│ (evaluator_   │
               │              │    + decision      │  agent.py)    │
               │              │
               │   deliver ◀──┤ final ≥ 0.75 and no trigger
               │              │
               │   fallback ─▶┌───────────────┐
               └──────────────│  FallbackAgent│──▶ context summary + simulated
                              │ (fallback_    │    booking link + 6 slots
                              │  agent.py)    │
                              └───────────────┘
```

| Agent | File | What it does |
|---|---|---|
| `ChatStyleAgent` | `src/digital_clone/agents/style_agent.py` | Learned the employee's email style from 7,414 usable sent Enron emails (8,926 raw sent-folder messages, 1,512 dropped by cleaning/sender match). 13 numeric features → StandardScaler → PCA → incremental EMA profile (`profile = (1−α)·profile + α·batch`, α = 0.3, 149 batches). Applies the learned greeting/sign-off (top patterns: "hi" 12.5% of emails, "thanks" 25.3%) and scores responses by raw-feature cosine similarity. |
| `RAGAgent` | `src/digital_clone/agents/rag_agent.py` | Retrieval-augmented answers from 500 computer-science textbooks chunked at 500/50 into 210,225 chunks, embedded with `all-MiniLM-L6-v2`, indexed in FAISS `IndexFlatIP` (L2-normalized = exact cosine). Retrieves top-5 with clipped similarities and generates a neutral factual answer with `[n] topic (chunk idx)` citations. |
| `EvaluatorAgent` | `src/digital_clone/agents/evaluator_agent.py` | Weighted quality gate: final = 0.4·style + 0.4·groundedness + 0.2·confidence; groundedness = `0.5·mean(top-k similarity) + 0.5·token overlap`; confidence = `0.6·relevance + 0.4·completeness − hedge penalty` (kept S7 reweight, see design decisions). Decision: deliver iff final ≥ 0.75 and no fallback trigger fires. |
| `FallbackAgent` | `src/digital_clone/agents/fallback_agent.py` | Trigger priority exactly `system_error → user_request → low_confidence → high_uncertainty`. Builds a context summary (query + reason + score breakdown), the simulated calendar link from `CloneConfig.calendar_link_template`, and 6 slots (next 3 weekdays × 10:00/14:00). |
| `PlannerAgent` | `src/digital_clone/agents/planner_agent.py` | Orchestration: retrieve → generate → apply_style → evaluate → deliver or fallback. Measures per-query latency (`time.perf_counter`), appends one JSONL line per query to the decision log, and converts any sub-agent exception into a graceful `system_error` fallback — never a crash. Exposed via `src/digital_clone/cli.py` (`--query` one-shot or interactive REPL). |

All tunables (weights, threshold, α, batch size, chunking, top_k, employee identity, booking template) live in `CloneConfig` (`src/digital_clone/config.py`); no call site hardcodes them.

## Setup

Requires Python 3.10+ (built and verified on 3.14.5; see [REPRODUCIBILITY.md](docs/REPRODUCIBILITY.md) for exact versions).

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/pip install -e .                  # so `python -m digital_clone` works from the repo root
.venv/bin/python -m digital_clone doctor    # environment self-check
.venv/bin/pytest                            # test suite (81 tests)
```

`crewai` is optional and **not** installed by `requirements.txt`: every release up to 1.15.24 requires Python <3.14, so on a 3.14 interpreter the optional `build_crew()` path cannot import it (see [CrewAI mapping](#crewai-mapping-spec-stack-item)).

## Full pipeline

From a clean clone, in this order (each script is idempotent; artifacts land under `data/`):

```bash
# 1. Style profile — downloads the Kaggle Enron corpus (~358 MB, cached via kagglehub),
#    prints the top-20 sent-volume report, learns the incremental profile.
.venv/bin/python scripts/build_style_profile.py
#    → data/models/style_profile_kay_mann.json (+ .joblib, gitignored)

# 2. Knowledge base — streams open-phi/textbooks (field filter "computer", 500 books),
#    chunks 500/50, embeds with MiniLM, builds the FAISS index. Measured 528.6 s on the
#    build machine (one-time offline cost — see known tensions).
.venv/bin/python scripts/build_knowledge_base.py
#    → data/rag/faiss_index/index.faiss + chunks_metadata.json (gitignored; >50 MB rule)
#    → data/rag/build_report.json (committed: chunk count, timings, 5 spot checks)

# 3. Interactive demo — REPL; or one-shot with --query.
.venv/bin/python -m digital_clone.cli
.venv/bin/python -m digital_clone.cli --query "What is TCP/IP?"

# 4. Evaluation — the fixed 20-query benchmark; regenerates the report.
#    NOTE: delete data/evaluations/decision_log.jsonl first if it exists — the planner
#    appends to it, and a stale log mixes runs.
.venv/bin/python scripts/run_evaluation.py
#    → data/evaluations/eval_results.json + decision_log.jsonl
#    → docs/evaluation_report.md (Steps 1–5 validation tables)

# 5. Visualizations — the 6 required PNGs from the evaluation artifacts.
.venv/bin/python scripts/make_visualizations.py
#    → docs/visualizations/*.png
```

Both large artifacts (FAISS index, 308 MB; chunk metadata, 102 MB) are gitignored per the >50 MB rule — step 2 rebuilds them. The committed `data/rag/build_report.json` and `data/evaluations/` files let you verify any rebuilt index against the published numbers.

## Tests

```bash
.venv/bin/pytest -v            # 81 tests, fully offline (fixtures + HashEmbedder)
.venv/bin/pytest --cov=digital_clone --cov-report=term-missing
```

81 tests: unit tests per agent, integration (planner), e2e (5 query types under 1 s), config/models, and the offline CrewAI mapping test. No test needs network, the real corpus, or the real index. Coverage: 99.3% of the deterministic pipeline core; 82% whole-package — the residual is entry points and real-data I/O exercised by the real builds instead (recorded honestly, not chased with test contortions).

## Results (kept configuration, after Stage 7 tuning)

20-query evaluation on the real pipeline (7,414-email style profile, 210,225-chunk FAISS index). Config: threshold 0.75, weights 0.4/0.4/0.2, confidence formula `0.6·relevance + 0.4·completeness − hedge penalty`, chunk 500/50, top_k 5.

| Metric | Target | Measured | Met? |
|---|---|---|---|
| Style score (mean) | > 0.90 | **0.999** | Yes |
| Groundedness (mean) | > 0.60 | **0.648** | Yes |
| Confidence (mean) | > 0.80 | **0.728** | **No** — see tension 1 |
| Final score (in-domain) | > 0.75 | **0.881** | Yes |
| Fallback rate | 30–40% | **40%** (4 `low_confidence` + 4 `user_request`) | Yes |
| End-to-end latency | < 1 s | **52 ms mean / 68 ms p95** (model + index load excluded per contract) | Yes |
| Reliability (20 queries) | > 95% | **100%** (0 crashes) | Yes |
| Retrieval time | < 1 s | 18 ms mean | Yes |
| Chunks indexed | > 900 | 210,225 | Yes |
| Indexing time | < 5 min | 528.6 s | **No** — see tension 4 |

Fallback rate by query type: in-domain factual 0/5, in-domain how-to 0/4, out-of-domain 1/4, ambiguous 3/3, booking requests 4/4. Full per-query tables: [docs/evaluation_report.md](docs/evaluation_report.md); raw results: [data/evaluations/eval_results.json](data/evaluations/eval_results.json) + `decision_log.jsonl` (one line per query). Tuning evidence: [docs/iteration_log.md](docs/iteration_log.md) — 4 entries (Stage 3 corpus note, baseline, kept reweight, rejected threshold), and the last "Keep? Yes" entry equals shipped `CloneConfig` defaults. Charts: [docs/visualizations/](docs/visualizations/) (6 PNGs).

## Design decisions

**Template-based response generation (no runtime LLM).** The graded pipeline must hit <1 s end-to-end latency (measured 52 ms mean) and run offline with deterministic, repeatable test results. An LLM round-trip per query would violate all three. Responses are assembled from retrieved chunks plus the learned greeting/sign-off; development assistance used LLMs, the runtime does not (user decision, 2026-10-06).

**Style score = raw-feature cosine.** The spec requires the PCA/EMA vector to store and track profile evolution, but scoring a single response against a scaled/PCA'd single-sample vector produces unstable cosines. So the persisted profile carries the PCA/EMA state (spec requirement), while scoring uses cosine similarity between the response's raw 13-feature vector and the profile's mean raw feature vector, clipped to [0,1] (documented in the system contract).

**Confidence formula reweight — provenance = iteration log Entry 2.** The spec's confidence pseudocode `0.5·relevance + 0.3·completeness − penalty` arithmetically caps at 0.8, below the >0.80 target. Baseline (spec formula) measured 0.572. The logged S7 experiment reweighted to `0.6·relevance + 0.4·completeness − penalty`: confidence rose to **0.728** with no met target regressing, and it was kept (`CloneConfig.confidence_relevance_weight = 0.6`, `confidence_completeness_weight = 0.4`). The residual gap to 0.80 is genuinely low retrieval relevance on ambiguous/out-of-domain queries, not a formula ceiling — a second experiment (threshold 0.70) that would have masked it was rejected and reverted (Entry 3).

**Corpus expansion (500 books, 210,225 chunks).** The assignment prescribes adjusting the corpus when spot checks return irrelevant chunks. The first build (smallest stop rule) selected 1 textbook → spot checks 1/5 relevant; 11,767 chunks → 2/5. The fix was a diversity floor of 500 computer-science books → 5/5 relevant, at the cost of indexing time (tension 4). Story and evidence: iteration log Stage 3 notes.

**CrewAI mapping (spec stack item).** `src/digital_clone/crew.py` maps all five agents onto CrewAI's Agent/Crew abstractions: `describe_crew()` returns the role/goal/backstory specs offline (tested in the suite), and `build_crew(planner)` constructs a real `crewai.Crew` only when `OPENAI_API_KEY` is set — the heavy `crewai` import lives inside that function, so the module imports cleanly where crewai can't be installed. The graded execution path never calls it: the deterministic planner is what satisfies the latency target and test determinism. Verified for real on a Python 3.13.5 side-venv (crewai 1.15.24 needs Python <3.14): `build_crew()` built a 5-agent Crew.

**Deliver vs fallback rationale (measured, per query type).**
- *In-domain factual/how-to (9/9 delivered, final 0.86–0.90):* the index holds closely matching textbook chunks, so relevance, groundedness, and confidence are all high — delivering is correct.
- *Booking requests (4/4 fallback, trigger `user_request`):* trigger priority fires before the score decision by design — the user explicitly asked for scheduling, so the correct behavior is the calendar fallback regardless of score.
- *Ambiguous (3/3 fallback, trigger `low_confidence`):* queries like "Tell me about it" have no retrievable referent; relevance collapses, confidence lands 0.47–0.58, below the 0.75 gate — falling back with a booking offer is the honest behavior.
- *Out-of-domain (1/4 fallback):* the intended behavior is fallback, and 3/4 still deliver (see tension 3).

## Known spec tensions (measured, not silently fixed)

1. **Confidence 0.728 < 0.80 target.** The spec formula caps at 0.8; the kept reweight (Entry 2) lifted it 0.572 → 0.728. Both prescribed knobs (formula reweight, and threshold changes that would shift the mix) are now exhausted — the residual is real low retrieval relevance on ambiguous/OOD queries. Recorded unmet.
2. **Fallback rate band 30–40% vs fixed 20-query mix.** 4/20 booking requests fall back by construction (20 pp floor). The kept threshold 0.75 lands the overall rate at 40% (in band). The tested 0.70 (Entry 3) reached 30% only by delivering every out-of-domain query, so it was rejected.
3. **Out-of-domain wrong delivery.** MiniLM finds superficially similar CS chunks, so 3/4 OOD queries clear the threshold and deliver (e.g., "Explain dark matter physics" at final 0.85). Flagged per the assignment's Step-4 repair note; no config knob improves it without worsening tensions 1–2 (Entry 3 evidence).
4. **Indexing time 528.6 s vs <5 min target.** The direct cost of the corpus expansion the assignment prescribes for irrelevant retrieval (smaller builds measured 1/5 and 2/5 relevant). One-time offline cost; query-time latency is 13–62 ms. Recorded unmet.
5. **Whole-package test coverage 82% < 90%.** The deterministic pipeline core is at 99.3%; the gap is entry points and real-data I/O paths (doctor, CLI wrapper, HF streaming loader, Enron CSV parser, embedder lazy paths) that the real S1–S3 builds exercised instead. Recorded as accepted-with-evidence, not hidden.

## Submission artifacts

- [docs/DELIVERABLE_CHECKLIST.md](docs/DELIVERABLE_CHECKLIST.md) — Final Success Criteria audited against real artifacts (34 met / 4 unmet with measured values)
- [docs/evaluation_report.md](docs/evaluation_report.md) — validation tables (assignment Steps 1–5)
- [docs/iteration_log.md](docs/iteration_log.md) — 4 entries; final config traceable to the last kept entry
- [docs/visualizations/](docs/visualizations/) — the 6 required charts
- [data/evaluations/](data/evaluations/) — raw results + decision logs (final run + per-experiment evidence)
- [data/models/style_profile_kay_mann.json](data/models/style_profile_kay_mann.json) — learned style profile
- [data/rag/build_report.json](data/rag/build_report.json) — knowledge-base build evidence
- [docs/REPRODUCIBILITY.md](docs/REPRODUCIBILITY.md) — dataset sources/hashes, exact versions, rebuild commands
