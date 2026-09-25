"""Grounded answer generation using retrieved context and Groq."""

import os

from dotenv import load_dotenv
from groq import Groq

from config import LLM_MODEL
from retrieve import retrieve

load_dotenv()

SYSTEM_PROMPT = """You are a personal Georgia Tech CompE course-planning assistant.
Answer the user's question using ONLY the provided course records.
Do not use outside knowledge or general facts about universities.
If the records do not contain enough information, say you don't have that in the collected course records.
Cite course codes. Keep answers concise and factual.
Do not mention instructors."""


def _format_context(chunks: list[dict]) -> str:
    parts = []
    for i, chunk in enumerate(chunks, 1):
        parts.append(
            f"[Excerpt {i} | source: {chunk['source']} | distance: {chunk['distance']:.3f}]\n"
            f"{chunk['text']}"
        )
    return "\n\n".join(parts)


def generate_answer(question: str, chunks: list[dict]) -> str:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key or api_key == "your_key_here":
        raise ValueError("Set GROQ_API_KEY in your .env file before generating answers.")

    client = Groq(api_key=api_key)
    context = _format_context(chunks)

    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    f"Question: {question}\n\n"
                    f"Document excerpts:\n{context}\n\n"
                    "Answer using only the course records above. Cite course codes."
                ),
            },
        ],
        temperature=0.1,
    )
    return response.choices[0].message.content.strip()


def ask(question: str, top_k: int | None = None) -> dict:
    from config import TOP_K

    k = top_k or TOP_K
    chunks = retrieve(question, top_k=k)
    answer = generate_answer(question, chunks)
    sources = sorted({chunk["source"] for chunk in chunks})
    return {
        "question": question,
        "answer": answer,
        "sources": sources,
        "chunks": chunks,
    }


def main() -> None:
    result = ask("Does CS 3251 have a lab, and what's its exam structure?")
    print("Answer:\n", result["answer"])
    print("\nSources:", ", ".join(result["sources"]))


if __name__ == "__main__":
    main()
