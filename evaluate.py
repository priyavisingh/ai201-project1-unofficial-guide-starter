"""Run the 5 evaluation questions and print results."""

from generate import ask

EVAL_QUESTIONS = [
    {
        "question": "What do students say about David Joyner's CS 1301 course structure and grading?",
        "expected": "Students praise self-paced structure, unlimited homework retries, multiple test attempts, and flexible scheduling.",
    },
    {
        "question": "Which professor do students recommend for CS 1332 and why?",
        "expected": "Frederic Faulkner is highly recommended because he explains when you need each data structure/algorithm before teaching it.",
    },
    {
        "question": "What complaints do students have about Thad Starner's AI courses?",
        "expected": "Minimal lecture content, self-teaching required, poor TA support, and lack of guidance in CS 3600/CS 6601.",
    },
    {
        "question": "How difficult is Konstantinos Dovrolis's CS 3510 according to reviews?",
        "expected": "Described as one of the hardest classes at Tech with strict partial credit; missing small details can cost 20%+ on grades.",
    },
    {
        "question": "What do students say about Jay Summet teaching CS 2200?",
        "expected": "Students report he rarely lectured, used daily clicker questions, and required reading 400+ textbook pages instead.",
    },
]


def main() -> None:
    for i, item in enumerate(EVAL_QUESTIONS, 1):
        print(f"\n{'=' * 70}")
        print(f"Question {i}: {item['question']}")
        print(f"Expected: {item['expected']}")
        result = ask(item["question"])
        print(f"\nSystem answer:\n{result['answer']}")
        print(f"\nSources: {', '.join(result['sources'])}")
        print("Retrieved chunks:")
        for j, chunk in enumerate(result["chunks"], 1):
            print(f"  [{j}] {chunk['source']} distance={chunk['distance']:.3f}")
            print(f"      {chunk['text'][:200]}...")


if __name__ == "__main__":
    main()
