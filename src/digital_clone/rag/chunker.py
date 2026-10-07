from langchain_text_splitters import RecursiveCharacterTextSplitter

from digital_clone.models import KnowledgeChunk


def chunk_documents(docs: list[dict], chunk_size: int = 500,
                    chunk_overlap: int = 50) -> list[KnowledgeChunk]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunks: list[KnowledgeChunk] = []
    for doc in docs:
        text = (doc.get("markdown") or "").strip()
        if not text:
            continue
        for piece in splitter.split_text(text):
            chunks.append(KnowledgeChunk(
                content=piece,
                source_topic=doc.get("topic") or "unknown",
                source_field=doc.get("field") or "unknown",
                chunk_index=len(chunks),
            ))
    return chunks
