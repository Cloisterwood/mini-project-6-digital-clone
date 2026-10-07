# scripts/build_knowledge_base.py
"""Build the FAISS knowledge base from open-phi/textbooks (computer science).

Stage 3 additions over July Task 12 Step 2:
- 5-query spot-check table (spec Step 2 validation: relevance in top-5,
  < 1 s per query) instead of the July 2-query smoke,
- per-phase timings (model load vs embedding+indexing vs save),
- writes data/rag/build_report.json with the measured numbers that later
  feed docs/evaluation_report.md (Step 2 validation table).

Run: python scripts/build_knowledge_base.py"""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from digital_clone.agents.rag_agent import RAGAgent
from digital_clone.config import CloneConfig
from digital_clone.rag.chunker import chunk_documents
from digital_clone.rag.corpus_loader import load_textbook_docs
from digital_clone.rag.embedder import SentenceEmbedder

# Spec Step 2 validation: 5 queries, each must surface a chunk containing
# its keyword in the top-5, each under 1 s.
SPOT_CHECKS = [
    ("What is TCP/IP?", "tcp"),
    ("How do databases index data?", "index"),
    ("What does Big-O notation measure?", "complexity"),
    ("How does Dijkstra's algorithm work?", "dijkstra"),
    ("What is DNS used for?", "dns"),
]


def main() -> None:
    cfg = CloneConfig()
    print("Streaming open-phi/textbooks (computer science entries)...")
    t0 = time.perf_counter()
    docs = load_textbook_docs(min_chunks=cfg.min_chunks,
                              chunk_size=cfg.chunk_size,
                              chunk_overlap=cfg.chunk_overlap)
    stream_s = time.perf_counter() - t0
    print(f"Selected {len(docs)} textbook entries in {stream_s:.1f}s.")
    fields = sorted({d["field"] for d in docs})
    topics = sorted({d["topic"] for d in docs})
    print(f"Fields: {fields}")
    print(f"First topics: {topics[:8]}")

    chunks = chunk_documents(docs, cfg.chunk_size, cfg.chunk_overlap)
    print(f"Produced {len(chunks)} chunks (target > {cfg.min_chunks}).")
    assert len(chunks) > cfg.min_chunks

    print("Loading SentenceEmbedder (all-MiniLM-L6-v2)...")
    t0 = time.perf_counter()
    embedder = SentenceEmbedder()
    model_s = time.perf_counter() - t0
    print(f"Model loaded in {model_s:.1f}s (dim={embedder.dim}).")

    print("Embedding + indexing (target < 5 minutes)...")
    agent = RAGAgent(embedder, cfg)
    t0 = time.perf_counter()
    agent.build(chunks)
    index_s = time.perf_counter() - t0
    t0 = time.perf_counter()
    agent.save()
    save_s = time.perf_counter() - t0
    print(f"Indexed {agent.index.size} chunks in {index_s:.1f}s "
          f"(+ {save_s:.1f}s save) -> {cfg.rag_dir / 'faiss_index'}")

    print("\nSpot-check table (relevance = expected keyword present in top-5):")
    rows = []
    for query, keyword in SPOT_CHECKS:
        t0 = time.perf_counter()
        top = agent.retrieve(query, k=5)
        ms = (time.perf_counter() - t0) * 1000
        relevant = any(keyword in r.chunk.content.lower() for r in top)
        rows.append({"query": query, "expected_keyword": keyword,
                     "top_topic": top[0].chunk.source_topic,
                     "top_similarity": round(top[0].similarity, 4),
                     "relevant_in_top5": relevant,
                     "latency_ms": round(ms, 1)})
        print(f"  {'PASS' if relevant and ms < 1000 else 'FAIL'}  "
              f"'{query}' -> top '{top[0].chunk.source_topic}' "
              f"(sim {top[0].similarity:.2f}, {ms:.0f} ms)")

    report = {
        "dataset": "open-phi/textbooks",
        "field_filter": "computer",
        "selected_docs": len(docs),
        "chunks": len(chunks),
        "min_chunks_target": cfg.min_chunks,
        "stream_seconds": round(stream_s, 1),
        "model_load_seconds": round(model_s, 1),
        "index_seconds": round(index_s, 1),
        "save_seconds": round(save_s, 1),
        "spot_checks": rows,
    }
    report_path = cfg.rag_dir / "build_report.json"
    report_path.write_text(json.dumps(report, indent=2))
    print(f"\nBuild report written to {report_path}")


if __name__ == "__main__":
    main()
