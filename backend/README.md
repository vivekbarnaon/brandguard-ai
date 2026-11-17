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
contract is intentionally configurable: `AIML_ANALYZE_PATH` accepts a JSON
payload containing `content_id`, `organisation_id`, `title`, and `content` and
must return `score` (0-100), `overall_status`, and a list `findings`.
Suggestions receive `content_id`, `organisation_id`, and `content`.
