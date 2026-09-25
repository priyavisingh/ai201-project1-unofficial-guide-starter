"""Retrieval-only evaluation. No LLM calls."""

import json
from pathlib import Path

from retrieve import retrieve

RESULTS_PATH = Path(__file__).parent / "eval_results.json"
TOP_K = 5

EVAL_QUESTIONS = [
    {
        "id": 1,
        "question": "Does CS 3251 have a lab, and what's its exam structure?",
        "expected_courses": ["CS 3251"],
        "acceptable_also": [],
        "required_facts": ["no lab", "midterm 25%", "programming quiz 12%", "final 32%"],
        "multi": False,
    },
    {
        "id": 2,
        "question": "What's the average GPA for CS 3510 and how are grades structured?",
        "expected_courses": ["CS 3510"],
        "acceptable_also": [],
        "required_facts": ["3.25", "four exams"],
        "multi": False,
    },
    {
        "id": 3,
        "question": "I don't want to take any exams. Does CS 3300 have a midterm or final?",
        "expected_courses": ["CS 3300"],
        "acceptable_also": [],
        "required_facts": ["no midterm or final", "quizzes"],
        "multi": False,
    },
    {
        "id": 4,
        "question": "Which course should I take to learn about operating systems design?",
        "expected_courses": ["CS 3210"],
        "acceptable_also": ["CS 4210"],
        "required_facts": ["CS 3210"],
        "multi": False,
    },
    {
        "id": 5,
        "question": "Which course teaches computer networking?",
        "expected_courses": ["CS 3251"],
        "acceptable_also": [],
        "required_facts": ["CS 3251"],
        "multi": False,
    },
    {
        "id": 6,
        "question": "I want to learn about caches and computer organization and architecture. Which course fits?",
        "expected_courses": ["ECE 4100"],
        "acceptable_also": ["CS 3220", "ECE 4180"],
        "required_facts": ["ECE 4100"],
        "multi": False,
    },
    {
        "id": 7,
        "question": "Which courses involve building embedded or physical devices?",
        "expected_courses": ["ECE 4180", "CS 3651", "CS 4220"],
        "acceptable_also": [],
        "required_facts": [],
        "multi": True,
        "note": "credit if any 2 of the 3 appear in top 5",
    },
    {
        "id": 8,
        "question": "I want a project-based Distributed Systems elective with no exams and a high average GPA. What are my options?",
        "expected_courses": ["CS 4605", "ECE 4795", "CS 3651"],
        "acceptable_also": [],
        "required_facts": [],
        "multi": True,
        "note": "credit if any 2 of the 3 appear in top 5",
    },
]


def _hit_codes(item: dict) -> set[str]:
    return set(item["expected_courses"]) | set(item.get("acceptable_also") or [])


def _recall_at_1(item: dict, sources: list[str]) -> bool | None:
    if item["multi"]:
        return None
    if not sources:
        return False
    return sources[0] in _hit_codes(item)


def _recall_at_5(item: dict, sources: list[str]) -> bool:
    found = [code for code in item["expected_courses"] if code in sources]
    if item["multi"]:
        return len(found) >= 2
    return bool(set(sources) & _hit_codes(item))


def _fact_coverage(item: dict, chunks: list[dict]) -> float | None:
    facts = item["required_facts"]
    if not facts:
        return None
    blob = "\n".join(chunk["text"] for chunk in chunks).lower()
    hits = sum(1 for fact in facts if fact.lower() in blob)
    return hits / len(facts)


def evaluate() -> dict:
    rows = []
    for item in EVAL_QUESTIONS:
        chunks = retrieve(item["question"], top_k=TOP_K)
        sources = [chunk["source"] for chunk in chunks]
        coverage = _fact_coverage(item, chunks)
        rows.append(
            {
                "id": item["id"],
                "question": item["question"],
                "retrieved": sources,
                "recall_at_1": _recall_at_1(item, sources),
                "recall_at_5": _recall_at_5(item, sources),
                "fact_coverage": coverage,
                "facts_found": [
                    fact
                    for fact in item["required_facts"]
                    if fact.lower() in "\n".join(c["text"] for c in chunks).lower()
                ],
                "facts_missing": [
                    fact
                    for fact in item["required_facts"]
                    if fact.lower() not in "\n".join(c["text"] for c in chunks).lower()
                ],
            }
        )

    single = [row for row in rows if row["recall_at_1"] is not None]
    with_facts = [row for row in rows if row["fact_coverage"] is not None]
    summary = {
        "recall_at_1": sum(1 for row in single if row["recall_at_1"]) / len(single),
        "recall_at_5": sum(1 for row in rows if row["recall_at_5"]) / len(rows),
        "mean_fact_coverage": (
            sum(row["fact_coverage"] for row in with_facts) / len(with_facts)
            if with_facts
            else None
        ),
        "n_recall_at_1": len(single),
        "n_fact_coverage": len(with_facts),
    }
    return {"results": rows, "summary": summary}


def _yn(value: bool | None) -> str:
    if value is None:
        return "n/a"
    return "yes" if value else "no"


def _fmt_coverage(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{value:.2f}"


def print_report(report: dict) -> None:
    print(f"{'Q':<3} {'R@1':<5} {'R@5':<5} {'Facts':<6} Retrieved")
    print("-" * 72)
    for row in report["results"]:
        retrieved = ", ".join(row["retrieved"])
        print(
            f"{row['id']:<3} {_yn(row['recall_at_1']):<5} {_yn(row['recall_at_5']):<5} "
            f"{_fmt_coverage(row['fact_coverage']):<6} {retrieved}"
        )
        print(f"    {row['question']}")
        if row["facts_missing"]:
            print(f"    missing facts: {', '.join(row['facts_missing'])}")
    summary = report["summary"]
    print("-" * 72)
    print(
        f"recall@1 {summary['recall_at_1']:.2f} "
        f"({summary['n_recall_at_1']} single-answer questions)"
    )
    print(f"recall@5 {summary['recall_at_5']:.2f} (8 questions)")
    print(
        f"mean fact coverage {summary['mean_fact_coverage']:.2f} "
        f"({summary['n_fact_coverage']} questions with required facts)"
    )


def main() -> None:
    report = evaluate()
    print_report(report)
    RESULTS_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"\nWrote {RESULTS_PATH.name}")


if __name__ == "__main__":
    main()
