# Enron Digital Clone (mini-project 6)

A deterministic five-agent "digital clone" of an Enron employee (default: Kay Mann) that answers questions in their email style, grounded in a computer-science textbook knowledge base, with weighted quality evaluation and calendar-booking fallback. No runtime LLM — the graded pipeline is fully deterministic and offline.

**Status:** Stage 1 in progress — environment, package skeleton, and data models. Stage plan: [docs/implementation/01-STAGES.md](docs/implementation/01-STAGES.md); system contract: [docs/implementation/02-SYSTEM-CONTRACT.md](docs/implementation/02-SYSTEM-CONTRACT.md).

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
| `EvaluatorAgent` | Weighted quality score: style 0.4 + groundedness 0.4 + confidence 0.2 |
| `FallbackAgent` | Calendar-booking fallback with simulated slots |
| `PlannerAgent` | Orchestration, latency, decision log, CLI |

Results and evaluation reports will be added here in Stages 6–8.
