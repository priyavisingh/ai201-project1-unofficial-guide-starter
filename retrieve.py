"""Semantic search over embedded professor review chunks."""

from sentence_transformers import SentenceTransformer

from config import EMBEDDING_MODEL, TOP_K
from embed_store import get_chroma_collection

_model: SentenceTransformer | None = None


def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(EMBEDDING_MODEL)
    return _model


def retrieve(query: str, top_k: int = TOP_K, where: dict | None = None) -> list[dict]:
    collection = get_chroma_collection()
    model = _get_model()
    query_embedding = model.encode([query]).tolist()

    query_kwargs = {
        "query_embeddings": query_embedding,
        "n_results": top_k,
        "include": ["documents", "metadatas", "distances"],
    }
    if where:
        query_kwargs["where"] = where

    results = collection.query(**query_kwargs)

    chunks = []
    for doc, meta, distance in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        chunks.append(
            {
                "text": doc,
                "source": meta["source"],
                "chunk_index": meta["chunk_index"],
                "distance": distance,
                "requirements_fulfilled": meta.get("requirements_fulfilled", ""),
                "skills_developed": meta.get("skills_developed", ""),
                "prerequisites": meta.get("prerequisites", ""),
                "exam_structure": meta.get("exam_structure", ""),
                "average_gpa": meta.get("average_gpa"),
            }
        )
    return chunks


def main() -> None:
    test_queries = [
        "What do students say about David Joyner's CS 1301 class?",
        "Who is the best professor for CS 1332 data structures?",
        "How difficult is Konstantinos Dovrolis's CS 3510?",
    ]
    for query in test_queries:
        print(f"\nQuery: {query}")
        for i, hit in enumerate(retrieve(query), 1):
            print(f"  [{i}] distance={hit['distance']:.3f} source={hit['source']}")
            print(f"      {hit['text'][:180]}...")


if __name__ == "__main__":
    main()
