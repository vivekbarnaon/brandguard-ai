# BrandGuard backend

This is the FastAPI backend for BrandGuard AI. It owns organisation data,
permissions, audit history, private guideline storage, and the human approval
workflow. AI/ML work remains in `aiml/` and is called through the configured
internal HTTP service.

## Setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Fill backend/.env with the database URL and server-only Supabase secret key.
alembic upgrade head
uvicorn app.main:app --reload
```

Never put `SUPABASE_SECRET_KEY`, database passwords, or AI credentials in
frontend code. The `brand-guidelines` bucket is private and is created by the
Alembic migration. Storage object paths must begin with the organisation UUID;
the migration adds organisation-membership policies for read/write/delete.

JWTs are verified against Supabase's project issuer and JWKS endpoint, which
supports projects using asymmetric signing. HS256 is supported only when
`SUPABASE_JWT_SECRET` is explicitly configured for a legacy project; the
publishable and secret API keys are not JWT signing secrets.

Interactive API documentation is available at `/docs`. The AI/ML service
paths are configurable with `AIML_ANALYZE_PATH` and
`AIML_SUGGESTIONS_PATH`. The typed boundary contracts are defined in
`app/schemas/aiml.py`: compliance requests carry `original_content` and
`guideline_context`, while suggestion requests carry the original content,
validated findings, guideline context, and rewrite mode.

## AIML backend integration

The `aiml/` directory remains the source of truth for Gemini, RAG, Qdrant,
compliance, and suggestion logic. The backend integration is being implemented
on this branch in `backend/` and must not duplicate or modify those modules.

The integration will be delivered in these stages:

1. Define typed backend adapters for compliance and suggestion results.
2. Load organisation-scoped guideline evidence before invoking AI/ML logic.
3. Send compliance requests using `original_content` and `guideline_context`,
   then validate and persist the generated report.
4. Send suggestion requests using `original_content`, validated findings,
   `guideline_context`, and an explicit rewrite mode.
5. Connect document processing and indexing to the upload workflow.
6. Add mocked integration tests for errors, tenant isolation, evidence
   validation, and human-review requirements.

The existing AIML contracts require evidence-backed results. AI output must
never approve content automatically, and suggestions must always remain
human-reviewable. No Gemini, Qdrant, Supabase secret, or database credential
may be exposed to the frontend or committed to Git.

### Current integration status

- Typed compliance and suggestion boundary models are implemented.
- Remote AI/ML responses are validated before the backend accepts them.
- Organisation-scoped guideline chunks are now stored through Alembic
  migration `0002_guideline_chunks`.
- Compliance and suggestion routes now load evidence from PostgreSQL rather
  than accepting guideline context from the frontend.
- The protected `POST /api/v1/documents/{document_id}/evidence` callback is
  available for the internal AIML processor and requires `AIML_INTERNAL_TOKEN`.
- The remaining integration step is connecting the actual PDF processor and
  Qdrant pipeline to this callback, followed by end-to-end tests.
