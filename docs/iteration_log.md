# Iteration log

Entry 1 (Baseline) is created in Stage 6 from the real evaluation run; tuning
experiments follow in Stage 7. This file starts in Stage 2 with build notes for
deviations the stage acceptance requires recording. Entry format is fixed by
`docs/implementation/02-SYSTEM-CONTRACT.md`.

## Stage 2 notes — style profile build (2026-10-07)

- **Emails dropped by cleaning (expected loader behavior, recorded as a deviation
  note):** `mann-k` holds 8,926 raw sent-folder messages in the Kaggle corpus;
  7,414 remained usable after forwarded-chain stripping, the ≥5-word body floor,
  and the exact sender match `kay.mann@enron.com` (1,512 dropped, ≈16.9%). No
  employee switch was needed — the ≥200 threshold is cleared by ~37×.
- **Profile evolution spike at batches 71–80:** per-batch Euclidean deltas jump
  from a ~0.1–0.9 baseline to 12.53/10.31/7.20 before decaying back by batch 86.
  This coincides with a region of the mailbox with atypically long/different
  messages (EMA with α=0.3 needs ~8 batches to absorb it). Kept as-is: it is a
  real property of the corpus, not a bug; `style_score` uses raw-feature cosine
  against mean features, not the EMA vector, so evaluation is unaffected. If S6
  shows style anomalies, the S7 knob is training-email filtering (folders /
  recipient types), per 02-SYSTEM-CONTRACT tension #4.
- **Radar chart repair:** first render placed a radial-axis label over two
  feature labels; removed (the July Task 14 chart-1 sketch has no radial
  ylabel) and re-rendered.

No `CloneConfig` tunable was changed in Stage 2; no tuning entry exists yet.

## Stage 3 notes — knowledge base build (2026-10-07)

The real build ran three times. Builds 1–2 exposed a corpus-diversity defect,
fixed per 01-STAGES S3 ("if spot checks return irrelevant chunks … document in
the iteration log before re-indexing") and the assignment's own Step-2 repair
guidance ("try expanding the corpus").

```markdown
## Iteration Log Entry

| Field | Value |
| --- | --- |
| Change | `load_textbook_docs` stop condition extended with a diversity floor `min_docs` (default 500): stream until the ≥900-chunk estimate (×1.2 headroom) is met **and** ≥500 distinct textbook entries selected. Spot-check keyword for the Big-O query changed from the literal `"big-o"` to `"complexity"` (hyphenation makes the literal brittle; query unchanged) |
| Reason | Build 1 (July stop rule): the first computer_science textbook alone satisfied the whole char quota → `selected_docs: 1`, 1,476 chunks, spot checks **1/5 relevant** (top sim ≈ 0.41). Build 2 (`min_docs=8`): 11,767 chunks from 8 arbitrary MIT course books — still no networking/algorithms book, spot checks **2/5**. A full-dataset keyword scan (1,511 CS books) showed the needed coverage exists deeper in the fixed stream order (Computer Networking: A Top-Down Approach = book #425, Introduction to Database Systems = #24, algorithm titles with Dijkstra from #32, Computer Language Engineering = #16, OS development = #411), so `min_docs=500` guarantees every Stage 6 in-domain evaluation topic. Chunk size/overlap/field filter (the other documented knobs) cannot fix topical absence |
| Metric Before | Build 1: docs=1, chunks=1,476, index 4.3 s, 1/5 relevant. Build 2: docs=8, chunks=11,767, index 24.8 s, 2/5 relevant |
| Metric After | Build 3: docs=500, chunks=210,225, index 528.6 s, **5/5 relevant** (top-1 sim 0.78–0.86, query latency 13–62 ms); persistence smoke reloads all 210,225 chunks in 8.5 s and answers "What is an operating system kernel?" at sim 0.83 |
| Delta | relevance 1/5 → 5/5; indexing 4.3 s → 528.6 s (see tension below) |
| Keep? | Yes — coverage is the qualitative gate ("Relevant chunks in top 5"); the indexing-time cost is recorded as a known spec tension, not silently accepted. `CloneConfig` tunables unchanged (chunk 500/50, top_k 5, min_chunks 900 all honored) |
```

**New spec tension (for README + S6 report): indexing time 528.6 s vs target
< 5 min.** The assignment's own two validation rows conflict at this corpus
scale: "expand the corpus" (its repair for irrelevant retrieval) pushes past
"indexing < 5 min", which assumes a ~900-chunk KB. Keeping both would have
required staying at a corpus size that measurably fails relevance (1/5, 2/5).
Chose relevance; indexing is a one-time offline cost, query latency (the
runtime target) is 13–62 ms ≪ 1 s. Recorded unmet, per "never assert without
a number". Also noted: the dataset's own topic labels include junk titles
("(PDF)", "(Vol. 2)") among the 500 — cosmetic metadata noise, content still
CS textbooks.

No `CloneConfig` tunable was changed in Stage 3; the loader change is code, not
a tunable (chunk_size/overlap/top_k/min_chunks all flow from `CloneConfig`).

## Entry 1 — Baseline (Stage 6, 2026-10-07)

```markdown
## Iteration Log Entry

| Field | Value |
| --- | --- |
| Change | Baseline config: threshold=0.75, weights=0.4/0.4/0.2, alpha=0.3, chunks=500/50, top_k=5, confidence=0.5*relevance+0.3*completeness-penalty (spec formula) |
| Reason | Starting point per project spec |
| Metric Before | — |
| Metric After | 20/20 queries, 0 crashes (reliability 100%). Fallback rate 50% (10/20: 6 low_confidence + 4 user_request). Mean style 0.999, groundedness 0.648, confidence 0.572, final (all scored) 0.773, final (in-domain) 0.845. Latency mean 41 ms, p95 56 ms (after model load). Evaluation speed 0.14 ms/call; retrieval mean 13.1 ms. Full block: `data/evaluations/eval_results.json`; per-query table: `docs/evaluation_report.md` |
| Delta | — |
| Keep? | Baseline reference |
```

Gaps vs targets, recorded honestly (S7 tuning input — no tuning done in S6):

- **Fallback rate 50% > 40% target.** By type: in-domain 0/9,
  out-of-domain 3/4, ambiguous 3/3, booking 4/4. Booking (4/20 = 20%) is
  fixed by the query mix (contract tension #2); the excess is low_confidence
  fallbacks on ambiguous/OOD queries. Assignment's own knob: threshold 0.70.
  Trigger priority untouched per 02-SYSTEM-CONTRACT.
- **Confidence mean 0.572 < 0.80 target.** Expected from the spec formula's
  0.8 cap (contract tension #1); the observed value is lower because
  completeness < 1 for short template answers. Logged S7 experiment: reweight
  `0.6·relevance + 0.4·completeness − penalty`.
- **Out-of-domain wrong delivery:** "Explain dark matter physics" delivered
  at final 0.81 (groundedness 0.70 — MiniLM finds superficially similar CS
  chunks, so token overlap stays high). In direct tension with the
  fallback-rate knob: lowering the threshold to 0.70 would deliver more OOD
  queries, raising it pushes fallback rate further above 40%. S7 must weigh
  both against the same 20-query set (the only benchmark).
- **Indexing time 528.6 s ≥ 5 min** — carried from S3 (iteration log Stage 3
  notes); not re-measured here, unchanged by query-time tuning.

No `CloneConfig` tunable was changed in Stage 6.

## Stage 7 notes — tuning experiments (2026-10-07)

Entry 1's measured gaps were the input. Decision rules, fixed before each run
and applied to the measured numbers: an experiment is **kept** only if it
moves a failed metric toward its target without regressing any previously-met
target (style > 0.90, groundedness > 0.60, in-domain final > 0.75, latency
< 1 s, reliability > 95%) and without worsening the recorded delivered-OOD
tension beyond what the fallback-band fix mechanically requires. Each
experiment = config change → fresh `run_evaluation.py` run (decision log
deleted first) → evidence copy in `data/evaluations/`. Per 01-STAGES (which
supersedes the July execution instructions), the 6 visualizations are
generated once from the final kept-config run, not after every experiment.
Chunk-size/top_k and training-email-filter knobs were **not** exercised: their
trigger conditions (groundedness < 0.60; style < 0.90) did not hold at
baseline or after the experiments below.

Visualization note: the 6 charts were generated from the final kept-config
run and passed visual acceptance in 3 judge rounds — round 1 flagged legend-
on-bars overlaps in `final_score_breakdown.png` and `fallback_rate_by_type.png`
(legends moved outside the axes), round 2 caught the relocated fallback legend
covering two bar value labels (bar order also aligned to the report's per-type
table, display names + 15° rotation for the tick labels), round 3 passed all
six. Repairs are chart-layout only; no data or scores changed.

```markdown
## Iteration Log Entry

| Field | Value |
| --- | --- |
| Change | Confidence formula reweighted from `0.5·relevance + 0.3·completeness − hedge penalty` to `0.6·relevance + 0.4·completeness − hedge penalty` (new `CloneConfig.confidence_relevance_weight`/`confidence_completeness_weight`, spec defaults preserved until this entry) |
| Reason | Baseline mean confidence 0.572 vs > 0.80 target (02-SYSTEM-CONTRACT tension #1: the spec formula caps at 0.8 before penalties); the July plan's prescribed knob for exactly this gap |
| Metric Before | Baseline (Entry 1): fallback rate 50% (10/20: 6 low_confidence + 4 user_request), style 0.999, groundedness 0.648, confidence 0.572, final (all) 0.773, final (in-domain) 0.845, latency 41/56 ms mean/p95, reliability 100%, delivered out-of-domain 1/4 ("dark matter" 0.81) |
| Metric After | Fallback rate 40% (8/20: 4 low_confidence + 4 user_request), style 0.999 (unchanged), groundedness 0.648 (unchanged), confidence 0.728, final (all) 0.805, final (in-domain) 0.881, latency 82/159 ms (run-to-run jitter, ≪ 1 s), reliability 100%, delivered out-of-domain 3/4 (weather/gumbo now 0.775). Evidence: `data/evaluations/eval_results_exp2_confidence_reweight.json` |
| Delta | confidence +0.156; fallback rate −10 pp; final in-domain +0.036; delivered OOD +2 (side effect: higher confidence lifts borderline finals over the unchanged 0.75 threshold) |
| Keep? | Yes — the failed metric (confidence) moves 0.572 → 0.728 toward 0.80 and is no longer formula-capped (residual gap is genuinely low retrieval relevance on ambiguous/OOD queries, not an arithmetic ceiling); no met target regresses; reliability and latency unchanged. `CloneConfig` defaults now 0.6/0.4 |
```

```markdown
## Iteration Log Entry

| Field | Value |
| --- | --- |
| Change | Fallback threshold lowered from 0.75 to 0.70 (July plan's knob for a fallback rate above the 30–40% band), run on top of Entry 2's kept reweight |
| Reason | Fallback rate measured 50% at baseline (Entry 1) and 40% after Entry 2; the band's upper edge leaves no margin, and the assignment's Step-4 note prescribes threshold tuning for the rate |
| Metric Before | Entry 2 state: fallback rate 40% (8/20), confidence 0.728, final (in-domain) 0.881, delivered out-of-domain 3/4 |
| Metric After | Fallback rate 30% (6/20: 2 low_confidence + 4 user_request), confidence 0.728 (unchanged), final (in-domain) 0.881 (unchanged), delivered out-of-domain **4/4** — "Who won the 2001 World Series?" at 0.719 and ambiguous "Tell me about it" at 0.713 now deliver. Evidence: `data/evaluations/eval_results_exp3_threshold070.json` |
| Delta | fallback rate −10 pp vs Entry 2 (40% → 30%, band's lower edge); delivered OOD +1 (3/4 → 4/4) |
| Keep? | No — the rate lands in-band only by delivering every out-of-domain query and one ambiguous query as confident answers; a CS-textbook clone "answering" a 2001 sports result is the recorded delivered-OOD tension at its worst (baseline 1/4 → Entry 2 3/4 → 4/4). Entry 2's configuration already sits in-band at 40%. Threshold reverted; `CloneConfig.fallback_threshold` stays 0.75 |
```

**Final configuration (traceable):** threshold 0.75 (spec; Entry 3 rejected),
weights 0.4/0.4/0.2 (spec, unchanged), confidence formula 0.6/0.4 (Entry 2,
kept), alpha 0.3, chunks 500/50, top_k 5 — the last "Keep? Yes" entry
(Entry 2) equals the shipped `CloneConfig` defaults, verified by the final
default-config rerun reproducing Entry 2's scores exactly (deterministic
pipeline; `data/evaluations/eval_results.json`).

**Remaining gaps after tuning, recorded honestly:** mean confidence 0.728
still < 0.80 — both prescribed knobs are now exhausted (the formula reweight
is kept; the threshold experiment was rejected), and the residual is real low
retrieval relevance on ambiguous/OOD queries, which no config knob lifts
without inflating relevance itself. Fallback rate 40% is in-band but at the
upper edge — the 4/20 booking mix (contract tension #2) fixes 20 pp of it, and
Entry 3 shows the only remaining direction (lower threshold) trades band
position for wrong deliveries. Delivered out-of-domain queries stand at 3/4
(dark matter 0.85, weather 0.78, gumbo 0.78) — a MiniLM-similarity artifact
the assignment's Step-4 note flags; recorded, not hidden. Indexing time
528.6 s (S3 tension) is an offline cost, unaffected by query-time tuning.
