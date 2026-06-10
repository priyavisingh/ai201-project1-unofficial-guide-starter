"""Gradio web UI for the Georgia Tech professor review guide."""

import gradio as gr

from generate import ask


def handle_query(question: str) -> tuple[str, str, str]:
    if not question.strip():
        return "Please enter a question.", "", ""
    result = ask(question.strip())
    sources = "\n".join(f"• {source}" for source in result["sources"])
    retrieval_debug = "\n\n".join(
        f"[{i}] {c['source']} (distance={c['distance']:.3f})\n{c['text'][:250]}..."
        for i, c in enumerate(result["chunks"], 1)
    )
    return result["answer"], sources, retrieval_debug


with gr.Blocks(title="GT Professor Review Guide") as demo:
    gr.Markdown(
        "# Georgia Tech Professor Review Guide\n"
        "Ask questions about CS professor reviews collected from Coursicle and student guides."
    )
    inp = gr.Textbox(
        label="Your question",
        placeholder="e.g., What do students say about CS 1332 with Frederic Faulkner?",
        lines=2,
    )
    btn = gr.Button("Ask", variant="primary")
    answer = gr.Textbox(label="Answer", lines=8)
    sources = gr.Textbox(label="Retrieved from", lines=4)
    retrieval = gr.Textbox(label="Top retrieved chunks (debug)", lines=10)

    btn.click(handle_query, inputs=inp, outputs=[answer, sources, retrieval])
    inp.submit(handle_query, inputs=inp, outputs=[answer, sources, retrieval])

if __name__ == "__main__":
    demo.launch()
