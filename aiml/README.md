# BrandGuard AI

The `aiml` project contains the AI and machine-learning components for
BrandGuard AI.

## Project structure

```text
aiml/
├── app/
│   ├── document_processor/  # PDF extraction and text cleaning
│   ├── embeddings/          # Chunking and Gemini embeddings
│   ├── vector_store/        # Qdrant storage and retrieval
│   ├── rag/                 # Grounded RAG pipeline
│   ├── compliance/          # Future compliance engine
│   └── suggestions/         # Future correction suggestions
├── tests/                   # AI/ML tests
├── data/                    # Local development documents
├── requirements.txt
├── .env.example
└── README.md
```

Backend application code belongs in the top-level `backend/` directory, not
inside `aiml/`. The `aiml/app/` package is reserved for AI/ML services.

## Gemini API setup

1. Change into the AI/ML directory:

   ```bash
   cd aiml
   ```

2. Activate the existing virtual environment:

   ```bash
   source venv/bin/activate
   ```

   On Windows PowerShell, use `venv\Scripts\Activate.ps1`.

3. Install the dependencies:

   ```bash
   python -m pip install -r requirements.txt
   ```

4. Put your Gemini API key in `aiml/.env`:

   ```dotenv
   GEMINI_API_KEY=your_actual_api_key
   GEMINI_MODEL=gemini-3.8-flash
   ```

   Never commit `.env` or put a real key in `.env.example`. The configured
   `gemini-3.8-flash` model is listed as a stable model in Google's current
   Gemini model documentation.

## Run the Gemini test

From the `aiml` directory, with the virtual environment activated:

```bash
python -m pytest tests/test_gemini.py -v
```

The test sends the prompt `Explain brand governance in two simple sentences.`
to Gemini and asserts that a non-empty response is returned. It is skipped
when `GEMINI_API_KEY` is not configured, so local test discovery does not
expose or require credentials.

## Common errors and troubleshooting

- **`GEMINI_API_KEY is missing`**: Create `aiml/.env` and set
  `GEMINI_API_KEY` to a valid key from Google AI Studio.
- **401/403 or unauthorised errors**: Check that the key is valid, the Gemini
  API is enabled for its project, and the request is allowed by the project's
  usage restrictions.
- **404 model not found**: Check `GEMINI_MODEL` against Google's supported
  model list and use the exact model ID.
- **429 resource exhausted**: Wait and retry, or review quota and billing
  limits for the API project.
- **Network or timeout errors**: Check connectivity and retry. The SDK may
  return transient service errors that should be handled by the caller.

## PDF document processing

Brand guideline PDFs can be processed page by page with PyMuPDF. The
processor validates the path, extracts text, cleans whitespace conservatively,
and preserves page numbers for future RAG evidence citations.

Install the dependencies from the `aiml` directory:

```bash
python -m pip install -r requirements.txt
```

Run the PDF extraction tests:

```bash
python -m pytest tests/test_pdf_extractor.py -v
```

Use the service from Python:

```python
from app.document_processor.processor import process_pdf

document = process_pdf("data/brand_guidelines.pdf")
```

Example result:

```python
{
    "document_name": "brand_guidelines.pdf",
    "total_pages": 2,
    "pages": [
        {"page_number": 1, "text": "Our brand voice should be professional."},
        {"page_number": 2, "text": "Avoid unsupported claims."},
    ],
    "status": "processed",
}
```

The current implementation extracts text layers only. Scanned or
image-only PDFs are detected as having no extractable text and will require
an OCR integration in a future task. Invalid, missing, non-PDF, and empty
inputs raise explicit processing errors.

## Text chunking and embeddings

Processed PDF pages are split with LangChain's
`RecursiveCharacterTextSplitter`. The default chunk size is 1,000 characters
with 150 characters of overlap. Both values can be configured when calling
`chunk_document`; paragraph and line separators are preferred before falling
back to spaces and individual characters.

Each chunk retains its document ID, filename, page number, global chunk index,
section, and source. Section is `None` when a heading cannot be identified
reliably.

Gemini's `gemini-embedding-001` is used for text embeddings. It returns
3,072-dimensional vectors and supports multiple text inputs per request. The
embedder batches requests, validates responses, and retries temporary SDK
failures. API keys are loaded from `.env` and are never included in chunk
metadata.

Run the unit tests, which use mocked Gemini responses:

```bash
python -m pytest tests/test_chunker.py tests/test_embedder.py -v
```

Example:

```python
from app.embeddings.chunker import chunk_document
from app.embeddings.embedder import GeminiEmbedder

chunks = chunk_document(processed_document, "brand-guidelines-001")
embedded_chunks = GeminiEmbedder().embed_chunks(chunks)
```

Qdrant storage is intentionally not included yet. Scanned PDF OCR is also
outside the current scope.

## Qdrant vector store

Qdrant stores the embedded chunks for semantic guideline retrieval. Configure
Qdrant Cloud or a local Qdrant instance in `aiml/.env`:

```dotenv
QDRANT_URL=your_qdrant_url
QDRANT_API_KEY=your_qdrant_api_key
QDRANT_COLLECTION=brand_guidelines
```

`QDRANT_API_KEY` may be empty for a local unauthenticated Qdrant instance.
Never commit `.env` or put real credentials in `.env.example`.

The collection uses cosine distance and the vector dimension from the
embedding returned by `GeminiEmbedder`; the existing collection is rejected
if its dimension differs. Each point payload contains:

- `text`
- `organization_id`
- `document_id`
- `document_name`
- `page_number`
- `chunk_index`
- `section`
- `source`

Store embedded chunks:

```python
from app.vector_store.qdrant_client import QdrantVectorClient
from app.vector_store.vector_store import QdrantVectorStore

qdrant = QdrantVectorClient()
qdrant.verify_connection()
store = QdrantVectorStore(qdrant)
point_ids = store.upsert_chunks(embedded_chunks, organization_id="org-001")
```

Retrieve relevant guidelines:

```python
from app.embeddings.embedder import GeminiEmbedder
from app.vector_store.retriever import QdrantRetriever

retriever = QdrantRetriever(qdrant, GeminiEmbedder())
results = retriever.search(
    "What tone should our campaign use?",
    organization_id="org-001",
    limit=5,
)
```

Organisation filtering is mandatory. An optional `document_id` filter
restricts retrieval to one uploaded document. Point IDs are deterministic
UUIDs derived from the organisation, document, and chunk index, so repeating
an upload upserts the same point instead of creating duplicates.

Run the mocked Qdrant tests:

```bash
python -m pytest \
  tests/test_qdrant_client.py \
  tests/test_vector_store.py \
  tests/test_retriever.py -v
```

## RAG pipeline

Retrieval-Augmented Generation (RAG) lets BrandGuard AI analyse submitted
content against an organisation's actual approved guidelines instead of asking
Gemini to rely on general knowledge. The pipeline embeds the submitted
content, retrieves tenant-filtered Qdrant chunks, preserves their source
references, and sends only that evidence plus the submitted content to Gemini.

The pipeline is implemented in
[`app/rag/rag_pipeline.py`](./app/rag/rag_pipeline.py) and the guarded prompt
is defined in [`app/rag/prompts.py`](./app/rag/prompts.py). The prompt treats
submitted content and retrieved text as untrusted data, requires JSON output,
separates explicit rules from inferred suggestions, and requires an
insufficient-evidence result instead of invented policies.

Example:

```python
from app.embeddings.embedder import GeminiEmbedder
from app.rag.rag_pipeline import RAGPipeline
from app.vector_store.qdrant_client import QdrantVectorClient
from app.vector_store.retriever import QdrantRetriever

qdrant = QdrantVectorClient()
retriever = QdrantRetriever(qdrant, GeminiEmbedder())
pipeline = RAGPipeline(retriever)

result = pipeline.analyze(
    organization_id="org-001",
    submitted_content="Our product is totally awesome!!!",
    top_k=5,
    score_threshold=0.75,
)
```

The returned object contains the structured Gemini analysis and evidence with
document ID, filename, page number, chunk ID, score, and original guideline
text. If no relevant chunks are retrieved, Gemini is not called and the
status is `no_relevant_guidelines`. Retrieval and generation failures are
raised explicitly.

Run the mocked RAG tests:

```bash
python -m pytest tests/test_rag_pipeline.py -v
```

This task does not implement the compliance engine or require a LangSmith
portal. LangSmith can be added later for optional tracing and evaluation.

## Brand compliance analysis

The compliance engine evaluates submitted content against the evidence
retrieved by the RAG pipeline. It does not retrieve new rules or make a final
approval decision. A human reviewer remains responsible for final approval.

Supported violation categories:

- `BRAND_VOICE`: tone, voice, or style conflicts
- `TERMINOLOGY`: incorrect approved product or brand terms
- `PROHIBITED_LANGUAGE`: disallowed words or phrases
- `UNSUPPORTED_CLAIM`: claims without supporting guideline evidence
- `PRODUCT_ACCURACY`: incorrect product descriptions or facts
- `DISCLAIMER`: missing or incorrect required disclaimers
- `MESSAGING`: conflicts with explicit messaging rules
- `OTHER`: evidence-backed issues outside the categories above

Severity levels:

- `CRITICAL`: potential legal, safety, regulatory, or materially harmful issue
- `HIGH`: clear explicit hard-rule, prohibited-language, or product-rule breach
- `MEDIUM`: meaningful terminology, tone, or messaging inconsistency
- `LOW`: minor wording or style issue with limited brand impact
- `INFO`: evidence-backed recommendation that is not a violation

Every finding must reference retrieved evidence. The engine attaches the
canonical document ID, filename, and page number from that evidence rather
than trusting model-supplied source details. Confidence is reported as an
estimated model confidence, not a statistically calibrated probability.

Example:

```python
from app.compliance.compliance_engine import ComplianceEngine

engine = ComplianceEngine()
result = engine.analyze(
    submitted_content="Our product guarantees 100% success.",
    guideline_context=rag_result["evidence"],
)
```

If no guideline evidence is available, the engine returns
`insufficient_evidence` without calling Gemini. Run the mocked compliance
tests with:

```bash
python -m pytest tests/test_compliance_engine.py -v
```

## Structured compliance reports

[`app/compliance/report_generator.py`](./app/compliance/report_generator.py)
converts compliance-engine findings into validated Pydantic models before
they are returned to the frontend. The report contract includes document and
organisation IDs, overall status, score, violation count, summary, findings,
source evidence, confidence, and a `human_review_required` flag.

The score starts at 100 and subtracts one penalty per unique issue:

```text
CRITICAL = 30
HIGH     = 20
MEDIUM   = 10
LOW      = 5
INFO     = 0
score = max(0, 100 - sum(unique_issue_penalties))
```

Duplicate findings with the same category, evidence chunk, and problematic
text are only penalised once. This score is an explainable review aid, not a
legal, statistical, or absolute compliance measure.

Statuses are determined as follows:

- `COMPLIANT`: no findings and the engine reported compliant.
- `NEEDS_REVIEW`: evidence-backed low or medium findings require review.
- `NON_COMPLIANT`: one or more high or critical findings require review.
- `INSUFFICIENT_EVIDENCE`: guideline evidence is missing or a finding lacks a
  source citation.

Every report sets `human_review_required` to `True`; no status grants final
approval. Generate and serialize a report:

```python
from app.compliance.report_generator import generate_report

report = generate_report(
    document_id="content-001",
    organisation_id="org-001",
    compliance_result=compliance_result,
)
frontend_payload = report.model_dump()
```

Run the report tests:

```bash
python -m pytest tests/test_report_generator.py -v
```

## Correction suggestions

[`app/suggestions/suggestion_engine.py`](./app/suggestions/suggestion_engine.py)
generates non-destructive corrections for evidence-backed compliance
findings. It accepts the original content, findings, and retrieved guideline
context, then asks Gemini for structured suggestions.

Supported rewrite modes:

- `minimal_correction`: make the smallest necessary change.
- `professional_rewrite`: improve professional wording while preserving meaning.
- `brand_aligned_rewrite`: align wording with the supplied brand voice and
  terminology.

The original content is never overwritten. Suggestions include the original
text, suggested text, reason, supporting rule, source evidence, and
`requires_human_review=true`. Findings without retrieved evidence are skipped
and reported as `insufficient_evidence`; the engine never invents citations,
facts, disclaimers, or guaranteed compliance.

Example:

```python
from app.suggestions.suggestion_engine import SuggestionEngine

engine = SuggestionEngine(text_generator=generate_text)
result = engine.generate(
    original_content=submitted_content,
    findings=compliance_result["findings"],
    guideline_context=rag_result["evidence"],
    mode="brand_aligned_rewrite",
)
frontend_payload = result.model_dump()
```

Run the mocked suggestion tests:

```bash
python -m pytest tests/test_suggestion_engine.py -v
```
