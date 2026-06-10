"""Embed chunks and store them in ChromaDB."""

import chromadb
from sentence_transformers import SentenceTransformer

from chunk import chunk_all_documents, load_chunks, save_chunks
from config import (
    CHROMA_DIR,
    CHUNKS_PATH,
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


def build_vector_store(chunks: list[dict] | None = None, reset: bool = True) -> int:
    chunks = chunks or chunk_all_documents()
    save_chunks(chunks)

    if reset and CHROMA_DIR.exists():
        client = chromadb.PersistentClient(path=str(CHROMA_DIR))
        try:
            client.delete_collection(COLLECTION_NAME)
        except ValueError:
            pass

    collection = get_chroma_collection()
    model = get_embedding_model()

    ids = [f"{c['source']}_{c['chunk_index']}" for c in chunks]
    documents = [c["text"] for c in chunks]
    metadatas = [{"source": c["source"], "chunk_index": c["chunk_index"]} for c in chunks]
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
