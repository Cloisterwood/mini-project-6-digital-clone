# System contract — formulas, thresholds, targets, data rules

Frozen at Stage 0. Every tunable lives in `CloneConfig`; call sites never hardcode these values. Any change to a tunable requires an iteration log entry (format at the end).

## Identity of the deliverable

Five plain-Python agents behind a deterministic planner, per the July plan's architecture:

- **ChatStyleAgent** — learns style from ≥200 sent Enron emails (13 numeric features → StandardScaler → PCA → EMA profile); scores style as cosine similarity; applies learned greeting/sign-off.
- **RAGAgent** — chunks `open-phi/textbooks` (computer-science filter) at 500/50, embeds with `all-MiniLM-L6-v2`, indexes in FAISS `IndexFlatIP` (L2-normalized = exact cosine), retrieves top-k, generates a neutral factual answer with citations.
- **EvaluatorAgent** — style (0.4) + groundedness (0.4) + confidence (0.2) → final score → deliver/fallback at 0.75.
- **FallbackAgent** — trigger priority `system_error → user_request → low_confidence → high_uncertainty`; produces context summary + simulated booking link + 6 slots.
- **PlannerAgent** — orchestration, latency measurement, JSONL decision log, graceful error recovery; exposed via CLI.

No runtime LLM and no network calls at query time (user decision 2026-10-06). Development assistance uses OpenAI Codex models; this is independent of the runtime.

## Fixed defaults (CloneConfig)

| Parameter | Value | Notes |
|---|---|---|
| style/groundedness/confidence weights | 0.4 / 0.4 / 0.2 | spec formula |
| fallback_threshold | 0.75 | deliver iff final ≥ threshold |
| alpha (EMA) / batch_size | 0.3 / 50 | incremental learning |
| chunk_size / chunk_overlap | 500 / 50 | spec default |
| top_k | 5 | retrieval |
| min_chunks | 900 | knowledge-base floor |
| expected_response_length | 400 chars | completeness score denominator |
| hedge_fallback_count | 3 | high_uncertainty trigger |
| employee | `kay.mann@enron.com`, folder `mann-k` | fallback employee `jeff.dasovich@enron.com`, `dasovich-j` |
| pca_components | 6 | capped by batch size at fit time |
| booking link / slots | `https://calendly.com/{employee_name}/30min`; 6 slots, next 3 weekdays 10:00 & 14:00 | simulated (user decision) |

## Metric definitions (binding)

- **Style score**: cosine similarity between the response's raw 13-feature vector and the profile's mean raw feature vector, clipped to [0,1]. The PCA/EMA vector stores and tracks profile evolution (spec requirement); raw-feature cosine is used for scoring because scaled/PCA'd single-sample vectors produce unstable cosines. Documented in README.
- **Groundedness**: `0.5·mean(top-k chunk similarity) + 0.5·(response-token ∩ chunk-token overlap ratio)`, clipped. Empty retrieval ⇒ 0.0.
- **Confidence**: spec pseudocode `0.5·relevance + 0.3·completeness − min(0.15·hedge_count, 0.5)`, clipped, where relevance = mean chunk similarity, completeness = `len(response)/expected_response_length` clipped. Hedge count counts matches of the phrase list ("i'm not sure", "might be", "possibly", "i think", …).
- **Final score**: weighted sum above, clipped. Decision: `deliver` iff final ≥ threshold AND no fallback trigger fires.
- **Latency**: `time.perf_counter` around `PlannerAgent.process(query)`, measured after planner construction (model load excluded, stated in the report).

## Targets (spec) — record measured values, never assert without a number

| Metric | Target |
|---|---|
| Style score (mean) | > 0.90 |
| Groundedness (mean) | > 0.60 |
| Confidence (mean) | > 0.80 |
| Final score (in-domain) | > 0.75 |
| Fallback rate | 30–40% |
| Chunks indexed | > 900 |
| Indexing time | < 5 min |
| Retrieval time | < 1 s |
| Evaluation speed | < 0.5 s |
| End-to-end latency (mean) | < 1 s |
| Reliability (20 queries, no crashes) | > 95% |
| Unit tests | ≥ 23 passing; coverage > 90% of core |
| Sent emails learned | ≥ 200 |
| Style features | ≥ 11 (plan: 13) |
| Visualizations | 6 PNGs |
| Iteration log | ≥ 3 entries, final config traceable |

## Known spec tensions and their resolutions (document these in README; do not silently "fix")

1. **Confidence target > 0.80 vs spec formula capped at 0.8** (max of `0.5·rel + 0.3·comp` = 0.8, minus penalties). Resolution: ship the spec formula at baseline; the reweight `0.6·rel + 0.4·comp − penalty` is a logged S7 experiment, kept only if the log says Keep.
2. **Fallback rate 30–40% vs fixed 20-query mix** (4/20 booking requests ⇒ ≥20% by construction). Resolution: report both the overall rate and the rate by query type; tuning knob is the threshold, never trigger priority.
3. **CrewAI in the required stack vs deterministic planner**. Resolution: `crew.py` maps all five agents onto CrewAI abstractions (`describe_crew`); the graded execution path stays deterministic because an LLM round-trip would break the <1s target and determinism of tests.
4. **Style score > 0.90 for template-wrapped text**: achievable because responses reuse the learned greeting/sign-off and profile-matched punctuation; if the mean lands below 0.90, the S7 knob is training-email filtering (folders/recipient types), logged.
5. **Latency < 1s includes no model load**: SentenceEmbedder loads once at planner construction. If per-query latency still exceeds 1s on the M2, profile before optimizing; the bottleneck would be embedding, and the fix is batching/caching, documented.
6. **Edge cases that must behave, not crash**: empty/malformed email bodies (loader returns None), empty retrieval (groundedness 0 → fallback), not-yet-learned profile (style score 0.0), sub-agent exception (graceful `system_error` fallback).

## Data rules

- Enron: only sent folders (`/sent`, `/_sent_mail`, `/sent_items`) of the configured employee, sender matched after parsing; forwarded chains and quote trailers stripped; bodies with <5 words dropped. The Kaggle CSV (`wcukierski/enron-email-dataset` via `kagglehub`, columns `file`, `message`) is the source; raw data is gitignored and never committed. Verify the license note in REPRODUCIBILITY.md before redistributing anything.
- Textbooks: `open-phi/textbooks` streamed, `field` containing "computer", entries shorter than one chunk skipped, stop at ≥900-chunk estimate with 20% headroom.
- Embeddings L2-normalized before add and search; all scores clipped to [0,1]; `chunk_index` globally sequential.
- Employee verification (S2): print a top-20 sent-volume report; require ≥200 usable emails for the chosen employee; switch only to the documented fallback, logged.

## Iteration log entry format (exact)

```markdown
## Iteration Log Entry

| Field | Value |
| --- | --- |
| Change | [what changed, e.g., "Adjusted fallback threshold from 0.75 to 0.70"] |
| Reason | [why, with the measured trigger] |
| Metric Before | [numbers] |
| Metric After | [numbers] |
| Delta | [signed] |
| Keep? | [Yes/No + reason] |
```

Baseline (Entry 1) records the S6 numbers. Every final configuration decision must trace to a specific entry; the last kept entry must equal `CloneConfig` defaults at delivery.

## Submission artifacts

README.md; `docs/evaluation_report.md`; `docs/iteration_log.md`; `docs/visualizations/` (6 PNGs); `data/models/style_profile_{employee}.json`; `data/rag/faiss_index/` + `chunks_metadata.json`; `data/evaluations/eval_results.json` + `decision_log.jsonl`; passing test suite; interactive CLI. `docs/DELIVERABLE_CHECKLIST.md` (S9) maps every spec checkbox to one of these paths.
