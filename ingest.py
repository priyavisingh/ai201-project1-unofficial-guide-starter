"""Load and clean professor review documents from the documents/ folder."""

import re
from pathlib import Path

from config import DOCUMENTS_DIR, RAW_DIR


# Patterns for junk copied from Coursicle pages — stripped during cleaning, not kept.
BOILERPLATE_PATTERNS = [
    r"🎥.*",
    r"Read all \d+ reviews.*",
    r"View .* Fall 2026 .*",
    r"Professors at Georgia Tech",
    r"CS at Georgia Tech",
    r"We're paying \$500/month.*",  # Coursicle TikTok recruitment ad
    r"Tap here to apply\.",
]


def clean_text(text: str) -> str:
    """Remove boilerplate, HTML entities, and extra whitespace."""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"&amp;", "&", text)
    text = re.sub(r"&nbsp;", " ", text)
    text = re.sub(r"&#39;", "'", text)
    text = re.sub(r"<[^>]+>", "", text)

    for pattern in BOILERPLATE_PATTERNS:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE)

    lines = [line.strip() for line in text.split("\n")]
    cleaned_lines = []
    for line in lines:
        if not line:
            if cleaned_lines and cleaned_lines[-1] != "":
                cleaned_lines.append("")
            continue
        cleaned_lines.append(line)

    return "\n".join(cleaned_lines).strip()


def load_documents(documents_dir: Path = DOCUMENTS_DIR) -> list[dict]:
    """Load all .txt documents and return structured records."""
    documents = []
    for path in sorted(documents_dir.glob("*.txt")):
        raw_text = path.read_text(encoding="utf-8")
        cleaned = clean_text(raw_text)
        if not cleaned:
            continue
        documents.append(
            {
                "source": path.name,
                "path": str(path),
                "text": cleaned,
            }
        )
    return documents


def save_raw_documents(documents: list[dict], output_dir: Path = RAW_DIR) -> None:
    """Persist cleaned text before chunking for inspection."""
    output_dir.mkdir(parents=True, exist_ok=True)
    for doc in documents:
        out_path = output_dir / doc["source"]
        out_path.write_text(doc["text"], encoding="utf-8")


def main() -> None:
    documents = load_documents()
    save_raw_documents(documents)
    print(f"Loaded {len(documents)} documents")
    if documents:
        print(f"\n--- Sample cleaned document: {documents[0]['source']} ---\n")
        print(documents[0]["text"][:800])
        if len(documents[0]["text"]) > 800:
            print("...")


if __name__ == "__main__":
    main()
