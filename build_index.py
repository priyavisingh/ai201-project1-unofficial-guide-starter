"""Run the full ingestion → chunking → embedding pipeline."""

from chunk import main as chunk_main
from embed_store import build_vector_store
from ingest import main as ingest_main


def main() -> None:
    print("=== Step 1: Ingest and clean documents ===")
    ingest_main()
    print("\n=== Step 2: Chunk documents ===")
    chunk_main()
    print("\n=== Step 3: Embed and store in ChromaDB ===")
    count = build_vector_store()
    print(f"\nDone. Indexed {count} chunks.")


if __name__ == "__main__":
    main()
