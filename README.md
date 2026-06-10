# The Unofficial Guide: Project 1

---

## Setup and Run

```bash
pip install -r requirements.txt
cp .env.example .env   # add your Groq API key
python build_index.py  # ingest → chunk → embed (921 chunks)
python app.py          # Gradio UI at http://localhost:7860
python evaluate.py     # run the 5 evaluation questions
```

---

## Domain

Georgia Tech professor reviews for CS and ECE courses. This knowledge is valuable because registration forces students to choose among multiple instructors for the same course number, and the decision depends on teaching style, exam difficulty, and workload which aren't always covered by official course descriptions. Oscar and Course Critique show what a course covers and sometimes grade distributions, but not whether lectures are useful, whether exams match homework, or which instructor students recommend. This system makes qualitative Coursicle reviews searchable so students can ask specific questions such as who to take for CS 1332 or how difficult CS 3510 is with a given professor.

---

## Document Sources

| # | Source | Type | URL or file path |
|---|--------|------|-----------------|
| 1 | David Joyner reviews | Coursicle professor page | https://www.coursicle.com/gatech/professors/David+Joyner/ |
| 2 | Frederic Faulkner reviews | Coursicle professor page | https://www.coursicle.com/gatech/professors/Frederic+Faulkner/ |
| 3 | Thad Starner reviews | Coursicle professor page | https://www.coursicle.com/gatech/professors/Thad+Starner/ |
| 4 | Charles Isbell reviews | Coursicle professor page | https://www.coursicle.com/gatech/professors/Charles+Isbell/ |
| 5 | Monica Sweat reviews | Coursicle professor page | https://www.coursicle.com/gatech/professors/Monica+Sweat/ |
| 6 | Mary Hudachek-Buswell reviews | Coursicle professor page | https://www.coursicle.com/gatech/professors/Mary+Hudachek-Buswell/ |
| 7 | Konstantinos Dovrolis reviews | Coursicle professor page | https://www.coursicle.com/gatech/professors/Konstantinos+Dovrolis/ |
| 8 | Daniel Forsyth reviews | Coursicle professor page | https://www.coursicle.com/gatech/professors/Daniel+Forsyth/ |
| 9 | CS 1332 course reviews | Coursicle course page | https://www.coursicle.com/gatech/courses/CS/1332/ |
| 10 | CS 2200 course reviews | Coursicle course page | https://www.coursicle.com/gatech/courses/CS/2200/ |
| 11 | CS 1301 course reviews | Coursicle course page | https://www.coursicle.com/gatech/courses/CS/1301/ |
| 12 | CS 4641 course reviews | Coursicle course page | https://www.coursicle.com/gatech/courses/CS/4641/ |
| 13 | Kevin Johnson reviews | Coursicle professor page | https://www.coursicle.com/gatech/professors/Kevin+Johnson/ |
| 14 | Pulkit Gupta reviews | Coursicle professor page | https://www.coursicle.com/gatech/professors/Pulkit+Gupta/ |
| 15 | GT professor review guide | Local text file | `documents/gt_professor_review_guide.txt` |

---

## Chunking Strategy

**Chunk size:** 400 characters

**Overlap:** 80 characters

**Why these choices fit your documents:**

Documents are short Coursicle reviews (1–3 sentences), not long guides. The chunker splits on `Review —` boundaries first so each review stays a complete thought, then applies sentence-level splitting only when a single review exceeds 400 characters. Each chunk is prefixed with header metadata (professor name, course, source URL). Before chunking, `ingest.py` strips Coursicle boilerplate (navigation text, "Read all N reviews" links, TikTok ads). An 80-character overlap prevents losing context when a fact spans two sentences.

**Corpus size:** 470 reviews across 15 documents (461 on 10 professor pages, 9 on 4 course pages, plus 1 summary guide)

**Final chunk count:** 921 chunks (~2 per review, because each chunk repeats document header metadata and the 400-character limit splits most reviews in two)

### Sample Chunks

**Chunk 1** (source: `cs_1332_course_reviews.txt`)
```
Review — Frederic Faulkner (Senior, FI, 11 months ago):
One thing I'll add to Professor Faulkner's list of compliments is how well he introduces ideas. He explains what situation you'd find yourself needing a data structure or algorithm before even teaching it- and this made understanding everything so much easier. He's a great professor.
```

**Chunk 2** (source: `david_joyner_reviews.txt`)
```
Review — CS 1301 (First-year, CEE, 3 years ago):
This is perhaps the best class I've taken. You can go at your own pace, and you cannot receive less than a one hundred on any homework assignment unless you give up. You get multiple attempts on test questions, and you can submit coding problems as many times as you want before you get it right.
```

**Chunk 3** (source: `thad_starner_reviews.txt`)
```
Review — CS 6601 (Graduate, CS, 3 years ago):
The course, the professor, and the TAs are a joke. There is no guidance or support, the lectures are borderline useless, and the TAs... well, they are awful at their jobs. They are utterly useless. They do not help, and don't have the students best interest in mind.
```

**Chunk 4** (source: `konstantinos_dovrolis_reviews.txt`)
```
Review — CS 3510 (First-year, MGT, 3 years ago):
Hardest class Ive ever taken at tech. If you miss 1 small thing, be prepared to lose at least 20% of your grade. For those who might think you are an exception and do well, YOU WONT. Avoid this class if possible
```

**Chunk 5** (source: `cs_2200_course_reviews.txt`)
```
Review — Jay Summet (First-year, CS, 3 years ago):
Nightmare of a class. I think he lectured once the whole class after there was an uproar midway through the semester about him never teaching. Just clicker questions EVERY day. Since he doesn't lecture and the clickers are awful, you have to read like 400+ pages in the dry textbook.
```

---

## Embedding Model

**Model used:** `all-MiniLM-L6-v2` via `sentence-transformers`, loaded locally with `SentenceTransformer("all-MiniLM-L6-v2")`. Stored in ChromaDB with cosine similarity search.

**Production tradeoff reflection:**

I used `all-MiniLM-L6-v2` because it runs locally with no extra API key or cost for embeddings, which made sense for this project. If I were actually deploying this for students during registration, I'd probably try a bigger model like `e5-large` since review text is pretty informal and easy to misread. I'd also think about whether local embeddings are fast enough once lots of people are querying at once.

---

## Retrieval Test Results

### Query 1: "What do students say about David Joyner's CS 1301 class?"

**Top returned chunks:**
1. `david_joyner_reviews.txt` (distance: 0.251): CS 1301 review praising self-paced structure and homework retries
2. `david_joyner_reviews.txt` (distance: 0.261): additional CS 1301 review on flexible online format
3. `david_joyner_reviews.txt` (distance: 0.264): review mentioning practice tests mirror real exams

**Why relevant:** All three chunks are from David Joyner's professor page and reference CS 1301. They contain themes the query asks about: self-paced structure, homework retries, and flexible scheduling.

### Query 2: "Which professor do students recommend for CS 1332 and why?"

**Top returned chunks:**
1. `monica_sweat_reviews.txt` (distance: 0.356): CS 1331 review ("best pick for CS 1331"), not CS 1332
2. `frederic_faulkner_reviews.txt` (distance: 0.358): Faulkner praised for dissecting hard topics and answering questions
3. `cs_1332_course_reviews.txt` (distance: 0.377): Faulkner review explaining he introduces when you need each data structure

**Why partially relevant:** The top chunk is about CS 1331, not CS 1332, but results 2 and 3 name Frederic Faulkner in the context of CS 1332 and describe his contextual teaching style. Generation still answers correctly because Faulkner chunks rank in the top-k set.

### Query 3: "How difficult is Konstantinos Dovrolis's CS 3510?"

**Top returned chunks:**
1. `gt_professor_review_guide.txt` (distance: 0.337): notes Dovrolis known for very difficult exams with strict grading
2. `konstantinos_dovrolis_reviews.txt` (distance: 0.420): CS 3510 review describing class as extremely hard
3. `konstantinos_dovrolis_reviews.txt` (distance: 0.429): review mentioning countless hours required

**Why partially relevant:** Chunks confirm CS 3510 is difficult with strict grading, but the top result is still a summary-style guide chunk rather than the specific review calling it the hardest class at Tech and complaining about harsh exam grading. Even after enriching the corpus, this retrieval weakness persists on evaluation question 4.

---

## Grounded Generation

**System prompt grounding instruction:**

```
You are a Georgia Tech student guide assistant.
Answer the user's question using ONLY the provided document excerpts.
Do not use outside knowledge, assumptions, or general facts about universities.
If the excerpts do not contain enough information, respond exactly with:
"I don't have enough information on that in the collected professor reviews."
Always mention which source file(s) support your answer.
Keep answers concise and factual.
```

The user message wraps retrieved chunks as numbered excerpts with source filenames and distance scores. The model is instructed again in the user turn to answer using only those excerpts and cite source file names. Temperature is set to 0.1 to reduce creative extrapolation.

**How source attribution is surfaced in the response:**

The LLM is instructed to name source files in its answer text (e.g., "source: frederic_faulkner_reviews.txt"). The Gradio UI also displays a separate "Retrieved from" field listing all source filenames programmatically from the retrieval step, independent of the LLM.

### Example Responses

**Example 1: grounded answer with attribution**

*Query:* "Which professor do students recommend for CS 1332 and why?"

*Response:* "Students recommend Professor Frederic Faulkner for CS 1332 because he explains concepts clearly and introduces ideas in a contextual manner, making it easier for students to understand. (source: cs_1332_course_reviews.txt, gt_professor_review_guide.txt, frederic_faulkner_reviews.txt)"

*Retrieved from:* cs_1332_course_reviews.txt, frederic_faulkner_reviews.txt, gt_professor_review_guide.txt

**Example 2: grounded answer with attribution**

*Query:* "What complaints do students have about Thad Starner's AI courses?"

*Response:* "Students complain that Thad Starner's AI courses require significant self-teaching, have minimal lectures, and poor TA support. They also describe the lectures as 'borderline useless' and state that there is no guidance or support. (thad_starner_reviews.txt)"

*Retrieved from:* thad_starner_reviews.txt

**Example 3: out-of-scope refusal**

*Query:* "What is the parking situation near the biology building?"

*Response:* "I don't have enough information on that in the collected professor reviews."

---

## Query Interface

The interface is a Gradio web app launched with `python app.py` at http://localhost:7860.

**Input fields:**
- "Your question": text box where the user types a natural-language question about GT professors or courses

**Output fields:**
- "Answer": grounded LLM response citing source files
- "Retrieved from": bulleted list of source document filenames
- "Top retrieved chunks (debug)": top-k chunks with distance scores for inspection

**Sample interaction:**

```
Question: What do students say about David Joyner's CS 1301 course structure and grading?

Answer: Students say the course structure is "well laid out" and the grading is "so
forgiving," with one student noting they only had to complete 3 problems on the final
for a 95 overall. (david_joyner_reviews.txt)

Retrieved from:
• david_joyner_reviews.txt
```

---

## Evaluation Report

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | What do students say about David Joyner's CS 1301 course structure and grading? | Self-paced; unlimited homework retries; multiple test attempts; flexible/beginner-friendly | Said course is "well laid out" with "forgiving" grading; mentioned final exam format but omitted self-paced structure and unlimited homework retries | Relevant | Partially accurate |
| 2 | Which professor do students recommend for CS 1332 and why? | Frederic Faulkner; explains when you'd need each data structure/algorithm before teaching it | Recommended Faulkner for making hard topics understandable and explaining when data structures are needed (frederic_faulkner_reviews.txt, cs_1332_course_reviews.txt) | Partially relevant | Accurate |
| 3 | What complaints do students have about Thad Starner's AI courses? | Minimal lectures; heavy self-teaching; poor/unhelpful TAs; little guidance | Complaints about unresponsive TAs, poor teaching, useless lectures, textbook reliance, learned more about Starner than AI (thad_starner_reviews.txt) | Relevant | Accurate |
| 4 | How difficult is Konstantinos Dovrolis's CS 3510 according to reviews? | Hardest class at Tech; exams are brutal with harsh partial credit; small mistakes cost you a lot | Said very difficult with strict grading and countless hours required; missed how punishing the exams feel | Partially relevant | Partially accurate |
| 5 | What do students say about Jay Summet teaching CS 2200? | Rarely lectured; daily clicker questions; 400+ pages of textbook reading | Described as nightmare class with minimal lecturing, clicker questions, 400+ pages of textbook reading (cs_2200_course_reviews.txt) | Relevant | Accurate |

**Retrieval quality:** Relevant / Partially relevant / Off-target  
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

**Question that failed:** How difficult is Konstantinos Dovrolis's CS 3510 according to reviews?

**What the system returned:** It got the general idea that CS 3510 is really hard with strict grading, but missed the more specific student complaint that exams are punishing. Like if you mess up one small thing on a problem, you can lose a huge chunk of credit and your grade tanks fast. It didn't really capture that vibe.

**Root cause (tied to a specific pipeline stage):** Even after adding 29 Dovrolis reviews and rebuilding the index (921 chunks total), retrieval still ranks `gt_professor_review_guide.txt` first at distance 0.342 instead of the actual student review calling it the hardest class at Tech. The guide chunk basically says the same thing in cleaner wording ("very difficult exams with strict grading"), so it wins semantic search over the angrier, more informal review. Chunking can also split long reviews across chunks, so the harshest lines might not all show up in the top 5 passed to the LLM.

**What you would change to fix it:** I'd probably stop splitting reviews mid-way and just let a `Review —` block stay whole even if it's a little over 400 characters. I'd also want professor review files to rank above the summary guide, or just pull more chunks so important details can make it into the LLM prompt.

---

## Spec Reflection

**One way the spec helped you during implementation:**

Writing the chunking strategy before coding forced me to think about review length and structure. Since I specified review-boundary splitting and 400-character chunks in planning.md, the implementation targeted complete reviews rather than arbitrary character cuts. The evaluation plan also gave me concrete test questions to run during Milestone 4 before adding generation, which surfaced the CS 3510 retrieval weakness early.

**One way your implementation diverged from the spec, and why:**

The spec described combining multiple sources (Coursicle, Reddit, Course Critique), but the initial implementation used Coursicle only because Reddit blocked automated fetching and Course Critique provides grade distributions rather than qualitative reviews. I added a student guidance document referencing Course Critique instead, and manually copied 461 professor-page reviews from Coursicle to address the coverage issue. 

---

## AI Usage

**Instance 1: Document collection with Claude**

- *What I gave the AI:* Coursicle URLs for 15 Georgia Tech professor and course pages, plus instructions to format each as a structured `.txt` file with `Review —` headers.
- *What it produced:* 15 document files in `documents/`, but only about two reviews per professor because Coursicle pages are JavaScript-rendered and automated fetching could not access the full review lists.
- *What I changed or overrode:* I identified that the small number of reviews caused evaluation question 4 (CS 3510 difficulty) to return only a partial answer. I manually copied 461 reviews across 10 professor pages from Coursicle, rebuilt the index (921 chunks), and re-ran evaluation. Q4 improved but still misses the harshest review details because the summary guide chunk outranks the actual student reviews.

**Instance 2: Pipeline implementation with Cursor/Claude**

- *What I gave the AI:* My planning.md sections (Chunking Strategy, Retrieval Approach, Architecture diagram) and Milestone 3–5 project requirements.
- *What it produced:* `ingest.py`, `chunk.py`, `embed_store.py`, `retrieve.py`, `generate.py`, and `app.py` wired together with ChromaDB and Groq.
- *What I changed or overrode:* I verified the chunk size matched my 400/80 spec, added Coursicle boilerplate removal patterns in `ingest.py`, and tightened the system prompt to require exact refusal wording for out-of-scope questions. I also added review-header reattachment logic in `chunk.py` after noticing chunks were splitting mid-review.
