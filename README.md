# BrandGuard AI

BrandGuard AI is an AI-powered brand governance platform that evaluates
marketing and business content against an organisation's approved brand
guidelines.

The project is being developed as a modular system with separate AI/ML,
backend, and frontend areas. The current implementation focuses on the
AI/ML foundation and is ready for backend API integration.

## What the system does

BrandGuard AI is designed to:

1. Accept brand guideline documents.
2. Extract text from PDF files while preserving page numbers.
3. Split extracted content into searchable chunks.
4. Generate Gemini embeddings for each chunk.
5. Store embeddings and source metadata in Qdrant.
6. Retrieve organisation-specific guideline evidence.
7. Analyse submitted content with a grounded Gemini RAG pipeline.
8. Produce evidence-linked compliance findings and structured reports.

The system does not make an irreversible legal or business approval decision.
Human reviewers retain final approval authority.

## Current project structure

```text
brandguard-ai/
├── aiml/
│   ├── app/
│   │   ├── document_processor/  # PDF extraction and text cleaning
│   │   ├── embeddings/          # Text chunking and Gemini embeddings
│   │   ├── vector_store/        # Qdrant storage and retrieval
│   │   ├── rag/                 # Grounded retrieval-augmented generation
│   │   ├── compliance/          # Compliance analysis and reports
│   │   └── suggestions/         # Future correction suggestions
│   ├── tests/                   # AI/ML automated tests
│   ├── data/                    # Local development documents
│   ├── requirements.txt
│   ├── .env.example
│   └── README.md                # AI/ML implementation details
├── backend/                     # Backend API implementation area
├── frontend/                    # Frontend implementation area
└── README.md
```

## AI/ML architecture

```text
PDF upload
  -> PDF text extraction
  -> Text cleaning
  -> Recursive text chunking
  -> Gemini document embeddings
  -> Qdrant vector storage

Submitted content
  -> Gemini query embedding
  -> Organisation-filtered Qdrant retrieval
  -> Grounded Gemini analysis
  -> Evidence-linked compliance findings
  -> Validated JSON compliance report
```

## Implemented components

### PDF document processing

The document processor uses PyMuPDF to extract text page by page. It validates
file paths, handles invalid and empty PDFs, and preserves page numbers for
future evidence citations. Scanned image-only PDFs currently require a future
OCR integration.

### Chunking and embeddings

LangChain's `RecursiveCharacterTextSplitter` creates chunks with a default
size of 1,000 characters and 150 characters of overlap. Gemini's dedicated
`gemini-embedding-001` model generates document and query embeddings.

### Qdrant vector storage

Qdrant stores vectors with the original text and source metadata. Retrieval
requires an organisation identifier, which enforces tenant isolation. Point
IDs are deterministic so repeated uploads safely upsert the same chunk.

### RAG pipeline

The RAG pipeline retrieves only organisation-specific evidence before asking
Gemini to analyse submitted content. The prompt treats submitted content and
retrieved text as untrusted data, prevents invented policies, and requires
structured evidence references.

### Compliance analysis

The compliance engine evaluates:

- Brand voice
- Terminology
- Prohibited language
- Unsupported claims
- Product accuracy
- Required disclaimers
- Messaging consistency
- Other evidence-backed issues

Findings include severity, explanation, confidence, source document, page
number, and evidence chunk ID. Confidence is an estimated model confidence,
not a statistically calibrated probability.

### Structured reports

Pydantic models validate the frontend response contract. Reports include:

- Compliance score
- Overall status
- Total violations
- Findings
- Evidence
- Suggested corrections
- Human review requirement

The score starts at 100 and applies configurable penalties for unique issues.
It is a transparent review aid, not a legal or absolute compliance measure.

## Local setup

### Requirements

- Python 3.9 or newer
- A Google Gemini API key
- A Qdrant Cloud cluster or local Qdrant instance

### Install dependencies

```bash
cd aiml
source venv/bin/activate
python -m pip install -r requirements.txt
```

On Windows PowerShell:

```powershell
cd aiml
venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

### Configure environment variables

Copy the example values into the local ignored `aiml/.env` file and replace
placeholders with valid credentials:

```dotenv
GEMINI_API_KEY=your_actual_api_key
GEMINI_MODEL=gemini-3.8-flash
GEMINI_EMBEDDING_MODEL=gemini-embedding-001
QDRANT_URL=your_qdrant_url
QDRANT_API_KEY=your_qdrant_api_key
QDRANT_COLLECTION=brand_guidelines
```

Never commit `aiml/.env`, API keys, confidential documents, virtual
environments, or generated caches.

## Run tests

Run the complete non-live AI/ML test suite:

```bash
cd aiml
source venv/bin/activate
python -m pytest \
  tests/test_pdf_extractor.py \
  tests/test_chunker.py \
  tests/test_embedder.py \
  tests/test_qdrant_client.py \
  tests/test_vector_store.py \
  tests/test_retriever.py \
  tests/test_rag_pipeline.py \
  tests/test_compliance_engine.py \
  tests/test_report_generator.py -v
```

The unit tests mock external Gemini and Qdrant calls where possible, so they
do not require API quota or insert test data into the production collection.
The separate Gemini integration test requires a valid local API key.

## Security and data handling

- Credentials are loaded from environment variables.
- API keys are excluded from Git.
- Organisation IDs are required during retrieval.
- Evidence is preserved instead of invented.
- Raw uncontrolled Gemini responses are not returned to the frontend.
- Final compliance decisions remain subject to human review.

## Current scope and next steps

The AI/ML foundation through structured compliance reports is implemented.
The top-level `backend/` directory is reserved for API endpoints and
application orchestration, while `frontend/` is reserved for the user
interface. OCR, correction suggestion workflows, backend APIs, frontend
screens, authentication, and production observability can be added in later
tasks.
