"""Split cleaned documents into retrieval-friendly chunks."""

import json
import re
from pathlib import Path

from config import CHUNK_OVERLAP, CHUNK_SIZE, CHUNKS_PATH
from ingest import load_documents


REVIEW_SPLIT = re.compile(r"(?=^Review — )", re.MULTILINE)


def _split_long_text(text: str, chunk_size: int, overlap: int) -> list[str]:
    if len(text) <= chunk_size:
        return [text]

    sentences = re.split(r"(?<=[.!?])\s+", text)
    chunks = []
    current = ""

    for sentence in sentences:
        candidate = f"{current} {sentence}".strip() if current else sentence
        if len(candidate) <= chunk_size:
            current = candidate
            continue
        if current:
            chunks.append(current)
        if len(sentence) <= chunk_size:
            current = sentence
        else:
            start = 0
            while start < len(sentence):
                end = start + chunk_size
                chunks.append(sentence[start:end].strip())
                if end >= len(sentence):
                    break
                start = max(end - overlap, start + 1)
            current = ""

    if current:
        chunks.append(current)
    return chunks


def _split_into_sections(text: str) -> list[str]:
    """Prefer review-level boundaries; fall back to paragraph splits."""
    if "Review —" in text:
        parts = [p.strip() for p in REVIEW_SPLIT.split(text) if p.strip()]
        return parts

    parts = [p.strip() for p in re.split(r"\n\n+", text) if p.strip()]
    return parts


def chunk_document(doc: dict, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[dict]:
    header_lines = []
    body_sections = []
    for section in _split_into_sections(doc["text"]):
        if section.startswith("Source:") or section.startswith("Professor:") or section.startswith("Course:"):
            header_lines.append(section)
        else:
            body_sections.append(section)

    header = "\n".join(header_lines)
    chunks = []

    for section in body_sections:
        section_text = f"{header}\n\n{section}" if header else section
        pieces = _split_long_text(section_text, chunk_size, overlap)
        review_prefix = ""
        if section.startswith("Review —"):
            review_prefix = section.split(":", 1)[0] + ":\n"

        for idx, piece in enumerate(pieces):
            text = piece.strip()
            if idx > 0 and review_prefix and review_prefix not in text:
                text = f"{header}\n\n{review_prefix}{text}" if header else f"{review_prefix}{text}"
            if len(text) < 40:
                continue
            chunks.append(
                {
                    "text": text,
                    "source": doc["source"],
                    "chunk_index": len(chunks),
                }
            )

    for i, chunk in enumerate(chunks):
        chunk["chunk_index"] = i

    return chunks


def chunk_all_documents(documents: list[dict] | None = None) -> list[dict]:
    documents = documents or load_documents()
    all_chunks = []
    for doc in documents:
        all_chunks.extend(chunk_document(doc))
    return all_chunks


def save_chunks(chunks: list[dict], path: Path = CHUNKS_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(chunks, indent=2), encoding="utf-8")


def load_chunks(path: Path = CHUNKS_PATH) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    chunks = chunk_all_documents()
    save_chunks(chunks)
    print(f"Created {len(chunks)} chunks from {len(load_documents())} documents")
    print("\n--- 5 sample chunks ---\n")
    for i, chunk in enumerate(chunks[:5], 1):
        print(f"[{i}] source={chunk['source']} index={chunk['chunk_index']}")
        print(chunk["text"][:300])
        print("-" * 60)


if __name__ == "__main__":
    main()
