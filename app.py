"""Gradio UI for the CompE course-planning tool."""

import gradio as gr

from generate import generate_answer
from retrieve import retrieve

EXAMPLES = [
    "Does CS 3251 have a lab, and what's its exam structure?",
    "Which course should I take to learn about operating systems design?",
    "I want to learn about caches and computer organization. Which course fits?",
]


def _title_from_chunk(text: str, code: str) -> str:
    first = text.split("\n", 1)[0]
    prefix = "Course: "
    if first.startswith(prefix):
        return first[len(prefix):].strip()
    return code


def _lab_label(text: str) -> str:
    for line in text.splitlines():
        if not line.startswith("Lab:"):
            continue
        raw = line[4:].strip().lower()
        if '"value": "yes"' in raw or raw.startswith("yes"):
            return "Has a lab"
        if '"value": "no"' in raw or raw.startswith("no"):
            return "No lab"
        return ""
    return ""


def _format_sources(chunks: list[dict]) -> str:
    if not chunks:
        return "No courses retrieved."
    seen = set()
    blocks = []
    for chunk in chunks:
        code = chunk["source"]
        if code in seen:
            continue
        seen.add(code)
        title = _title_from_chunk(chunk["text"], code)
        gpa = chunk.get("average_gpa")
        facts = []
        if isinstance(gpa, (int, float)) and gpa >= 0:
            facts.append(f"GPA {gpa:.2f}")
        lab = _lab_label(chunk["text"])
        if lab:
            facts.append(lab)
        exam = (chunk.get("exam_structure") or "").strip()
        fact_line = " · ".join(facts)
        exam_line = f"\n\nExams: {exam}" if exam and exam != "not specified" else ""
        blocks.append(f"**{title}**\n\n{fact_line}{exam_line}")
    return "\n\n".join(blocks)


def _format_debug(chunks: list[dict]) -> str:
    if not chunks:
        return ""
    return "\n\n".join(
        f"[{i}] {chunk['source']} (distance={chunk['distance']:.3f})\n{chunk['text']}"
        for i, chunk in enumerate(chunks, 1)
    )


def handle_query(question: str) -> tuple[str, str, str]:
    if not question or not question.strip():
        return "Enter a question about a course, a skill, or a requirement.", "", ""
    chunks = retrieve(question.strip())
    sources = _format_sources(chunks)
    debug = _format_debug(chunks)
    try:
        answer = generate_answer(question.strip(), chunks)
    except Exception as exc:
        answer = f"Could not generate an answer. {exc}"
    return answer, sources, debug


theme = gr.themes.Soft(
    primary_hue="blue",
    neutral_hue="slate",
    font=["ui-sans-serif", "system-ui", "-apple-system", "Segoe UI", "sans-serif"],
    font_mono=["ui-monospace", "SFMono-Regular", "Menlo", "monospace"],
)

with gr.Blocks(title="GT CompE Course Planner") as demo:
    gr.Markdown(
        "# GT CompE Course Planner\n"
        "A personal course-planning tool built from public Georgia Tech catalog and syllabus data. Not an official Georgia Tech service."
    )
    question = gr.Textbox(
        label="Question",
        placeholder="Ask which course fits a skill, or how a course is graded.",
        lines=2,
    )
    gr.Examples(
        examples=EXAMPLES,
        inputs=question,
        label="Try an example",
        run_on_click=False,
    )
    ask_button = gr.Button("Ask", variant="primary")
    gr.Markdown("### Answer")
    answer = gr.Markdown()
    gr.Markdown("### Sources")
    sources = gr.Markdown()
    with gr.Accordion("Show details", open=False):
        details = gr.Textbox(label="Retrieved chunks", lines=12)

    ask_button.click(handle_query, inputs=question, outputs=[answer, sources, details])
    question.submit(handle_query, inputs=question, outputs=[answer, sources, details])


if __name__ == "__main__":
    demo.launch(theme=theme)
