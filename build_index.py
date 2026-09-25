"""Run the full ingestion → chunking → embedding pipeline."""

from chunk import chunk_courses, save_chunks
from embed_store import build_vector_store
from ingest import load_courses


def main() -> None:
    print("=== Step 1: Load course records ===")
    courses = load_courses()
    print(f"Loaded {len(courses)} courses")
    print("\n=== Step 2: Chunk once, one course per chunk ===")
    chunks = chunk_courses(courses)
    save_chunks(chunks)
    print(f"Created {len(chunks)} chunks")
    print("\n=== Step 3: Embed and store in ChromaDB ===")
    count = build_vector_store(chunks)
    print(f"\nDone. Indexed {count} chunks.")


if __name__ == "__main__":
    main()
