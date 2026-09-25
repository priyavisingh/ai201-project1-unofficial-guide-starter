"""Embed chunks and store them in ChromaDB."""

import chromadb
from sentence_transformers import SentenceTransformer

from chunk import load_chunks, save_chunks
from config import (
    CHROMA_DIR,
    COLLECTION_NAME,
    EMBEDDING_MODEL,
)


def get_embedding_model() -> SentenceTransformer:
    return SentenceTransformer(EMBEDDING_MODEL)


def get_chroma_collection():
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )


FILTER_FIELDS = (
    "requirements_fulfilled",
    "skills_developed",
    "prerequisites",
    "exam_structure",
    "average_gpa",
)


def _metadata(chunk: dict) -> dict:
    meta = {"source": chunk["source"], "chunk_index": chunk["chunk_index"]}
    for field in FILTER_FIELDS:
        value = chunk.get(field, "not specified")
        if field == "average_gpa":
            meta[field] = float(value) if isinstance(value, (int, float)) else -1.0
        else:
            meta[field] = str(value)
    return meta


def build_vector_store(chunks: list[dict] | None = None, reset: bool = True) -> int:
    # Use the chunks already built. Do not chunk again.
    chunks = chunks if chunks is not None else load_chunks()
    save_chunks(chunks)

    if reset and CHROMA_DIR.exists():
        client = chromadb.PersistentClient(path=str(CHROMA_DIR))
        try:
            client.delete_collection(COLLECTION_NAME)
        except Exception:
            pass

    collection = get_chroma_collection()
    model = get_embedding_model()

    ids = [f"{c['source']}_{c['chunk_index']}" for c in chunks]
    documents = [c["text"] for c in chunks]
    metadatas = [_metadata(c) for c in chunks]
    embeddings = model.encode(documents, show_progress_bar=True).tolist()

    collection.add(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
        embeddings=embeddings,
    )
    return len(chunks)


def main() -> None:
    count = build_vector_store()
    print(f"Stored {count} chunks in ChromaDB at {CHROMA_DIR}")


if __name__ == "__main__":
    main()
