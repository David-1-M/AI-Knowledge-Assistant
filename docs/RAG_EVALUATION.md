# RAG Evaluation Protocol

This document describes a repeatable **manual evaluation process** for the AI-Powered Knowledge Assistant. It is a proposed test protocol, not a claim that benchmark results have already been obtained.

## Goal

Evaluate whether the application retrieves relevant passages, answers questions using the uploaded PDF, gives useful page references, and avoids inventing answers when evidence is missing.

## Prepare an evaluation set

Use a small collection of **non-sensitive**, text-based PDFs that you have permission to process. Create at least 15 question-answer cases:

| Category | Suggested cases | What to check |
|---|---:|---|
| Direct factual lookup | 5 | A clear answer is present in the PDF |
| Multi-passage synthesis | 4 | Correctly combines evidence from several passages |
| Unanswerable question | 3 | Acknowledges insufficient document evidence |
| Ambiguous wording | 2 | Avoids unsupported assumptions |
| Page citation | 1 | Reference points to the passage supporting the answer |

For each case, record the PDF name, question, expected evidence, expected page(s), and a short human-written reference answer.

## Running the evaluation

1. Start Ollama, FastAPI, and the Streamlit frontend using the README instructions.
2. Upload and index the evaluation PDF.
3. Select only the relevant document in the interface.
4. Ask each prepared question exactly as written.
5. Capture the generated answer, retrieved sources, page references, and any errors.
6. Repeat tests on the same dataset after meaningful changes to chunking, embeddings, retrieval, prompt instructions, or model version.

## Scoring rubric

Score each dimension from **0 to 2**.

| Dimension | 0 | 1 | 2 |
|---|---|---|---|
| Answer correctness | Incorrect or absent | Partially correct | Correct and complete |
| Grounding | Unsupported claims | Mixed support | Material claims supported by retrieved text |
| Source relevance | Irrelevant passages | Partly relevant | Passages directly support the answer |
| Citation accuracy | Incorrect or missing | Partly correct | Correct document/page reference |
| Abstention (unanswerable cases) | Fabricates answer | Expresses uncertainty but guesses | Clearly states evidence is insufficient |

For a single test case, use only applicable dimensions. Calculate:

`normalized_score = points_earned / (2 * applicable_dimension_count)`

Do not compare scores across different datasets without documenting the changed questions, PDFs, and scoring criteria. Report results by category as well as overall.

## Results template

| Case ID | Category | Correctness | Grounding | Relevance | Citation | Abstention | Notes |
|---|---|---|---|---|---|---|---|
| Q01 | Direct lookup | — | — | — | — | N/A | Not yet evaluated |

Also record:
- Date, Git commit SHA, Python version, embedding model, Ollama model, and PDF corpus revision.
- Total questions, applicable rubric scores, and failures.
- Latency observations, if measured consistently on the same machine.
- Any changes made after evaluating.

## Limitations

- A cited retrieved passage does **not** automatically prove that the answer is correct.
- A small test set can reveal regressions but is not a comprehensive benchmark.
- Generated outputs may vary between repeated runs.
- Scanned PDFs are not covered by the current text-based extraction workflow.
- Do not upload confidential documents or personally identifiable information into a shared evaluation dataset.

## Next engineering steps

Turn the saved question set into machine-readable fixtures, add deterministic retrieval tests with mocked embeddings, and evaluate groundedness and abstention separately from answer fluency.
