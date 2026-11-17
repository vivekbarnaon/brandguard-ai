from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.routes import approvals, auth, compliance, content, dashboard, documents, organisations, suggestions

app = FastAPI(title="BrandGuard AI Backend", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=[get_settings().frontend_url], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
for router in (auth.router, organisations.router, documents.router, content.router, compliance.router, suggestions.router, approvals.router, dashboard.router):
    app.include_router(router, prefix="/api/v1")


@app.get("/health")
async def health():
    return {"status": "ok"}

