# Enron Digital Clone (mini-project 6)

A deterministic five-agent "digital clone" of an Enron employee (default: Kay Mann) that answers questions in their email style, grounded in a computer-science textbook knowledge base, with weighted quality evaluation and calendar-booking fallback. No runtime LLM — the graded pipeline is fully deterministic and offline.

**Status:** Stages 0–7 complete (2026-10-07) — baseline evaluation, 2 logged tuning experiments, and the 6 required visualizations are done; Stage 8 (CrewAI mapping, reproducibility) and Stage 9 (delivery checklist) remain. Stage plan: [docs/implementation/01-STAGES.md](docs/implementation/01-STAGES.md); system contract: [docs/implementation/02-SYSTEM-CONTRACT.md](docs/implementation/02-SYSTEM-CONTRACT.md).

## Quick start

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/pip install -e .
.venv/bin/python -m digital_clone doctor   # environment self-check
.venv/bin/pytest                            # test suite
```

## Architecture

| Agent | Role |
|---|---|
| `ChatStyleAgent` | Learns the employee's email style (13 numeric features → StandardScaler → PCA → EMA profile) |
| `RAGAgent` | Retrieval-augmented answers from the textbook corpus (chunk 500/50, MiniLM embeddings, FAISS) |
| `EvaluatorAgent` | Weighted quality score: style 0.4 + groundedness 0.4 + confidence 0.2; confidence = `0.6·relevance + 0.4·completeness − hedge penalty` (kept S7 reweight — see tensions below) |
| `FallbackAgent` | Calendar-booking fallback with simulated slots |
| `PlannerAgent` | Orchestration, latency, decision log, CLI |

## Results (kept configuration, Stage 7)

20-query evaluation on the real pipeline (7,414-email style profile, 210,225-chunk FAISS index): reliability 100%, latency ≪ 1 s (model load excluded), style 0.999, groundedness 0.648, confidence 0.728, in-domain final 0.881, fallback rate 40%. Full tables: [docs/evaluation_report.md](docs/evaluation_report.md); tuning evidence: [docs/iteration_log.md](docs/iteration_log.md) (baseline + 2 experiments, final config traceable to the last kept entry); charts: [docs/visualizations/](docs/visualizations/) (6 PNGs).

## Known spec tensions (measured, not silently fixed)

1. **Confidence target > 0.80 vs spec formula cap 0.8** — kept the logged S7 reweight `0.6·relevance + 0.4·completeness − penalty` (iteration log Entry 2): confidence rose 0.572 → 0.728. The residual gap is genuinely low retrieval relevance on ambiguous/out-of-domain queries, not a formula ceiling; still recorded unmet.
2. **Fallback rate band 30–40% vs fixed 20-query mix** — 4/20 booking requests fall back by construction (20 pp floor). Kept threshold 0.75 lands the rate at 40% (in band). The tested alternative (0.70, iteration log Entry 3) reached 30% only by delivering every out-of-domain query, so it was rejected.
3. **Out-of-domain wrong delivery** — MiniLM finds superficially similar CS chunks, so 3/4 OOD queries score above the threshold and deliver (e.g., "Explain dark matter physics" at 0.85). Flagged per the assignment's Step-4 repair note; no config knob fixes it without worsening metrics 1–2 (Entry 3 evidence).
4. **Indexing time 528.6 s vs < 5 min target** — the cost of the corpus expansion the assignment prescribes for irrelevant retrieval (smaller builds measured 1/5 and 2/5 relevant). One-time offline cost; query latency is 13–16 ms.
