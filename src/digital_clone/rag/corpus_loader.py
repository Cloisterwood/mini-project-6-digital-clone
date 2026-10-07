"""Load open-phi/textbooks filtered to a coherent domain. Only used by
scripts/ — unit tests never import this (network dependency).

Deviation from the July code (docs/iteration_log.md, Stage 3): the stop
condition adds a diversity floor `min_docs`. The July rule (stop at the
≥min_chunks char estimate with 20% headroom) is satisfiable by one huge
textbook, which starves the KB of topical breadth and fails the spec's
Step 2 spot checks. min_docs=500 is the smallest round prefix whose
stream-order books cover every Stage 6 in-domain evaluation topic
(networking at book #425, databases #24, algorithms #32+, compilers #16,
OS development #411); a full-dataset keyword scan evidences this in the
iteration log."""


def load_textbook_docs(min_chunks: int = 900, chunk_size: int = 500,
                       chunk_overlap: int = 50,
                       field_filter: str = "computer",
                       min_docs: int = 500) -> list[dict]:
    from datasets import load_dataset  # lazy heavy import

    ds = load_dataset("open-phi/textbooks", split="train", streaming=True)
    docs: list[dict] = []
    total_chars = 0
    stride = max(chunk_size - chunk_overlap, 1)
    for row in ds:
        field = (row.get("field") or "").lower()
        if field_filter not in field:
            continue
        text = row.get("markdown") or ""
        if len(text) < chunk_size:
            continue
        docs.append({"markdown": text, "topic": row.get("topic") or "unknown",
                     "field": row.get("field") or "unknown"})
        total_chars += len(text)
        if (total_chars / stride >= min_chunks * 1.2  # 20% headroom
                and len(docs) >= min_docs):
            break
    return docs
