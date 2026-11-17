from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies.auth import current_user
from app.models import ComplianceReport, Content, User
from app.schemas.aiml import SuggestionRequest
from app.routes.content import get_content
from app.services.aiml import generate_suggestions, retrieve_guidelines

router = APIRouter(prefix="/suggestions", tags=["suggestions"])


@router.post("/generate")
async def generate(content_id: UUID, user: Annotated[User, Depends(current_user)], db: Annotated[AsyncSession, Depends(get_db)]):
    content = await get_content(content_id, db, user.id)
    report = await db.scalar(
        select(ComplianceReport)
        .where(ComplianceReport.content_id == content.id)
        .order_by(ComplianceReport.created_at.desc())
    )
    if report is None:
        raise HTTPException(status_code=409, detail="Analyze content before generating suggestions")
    evidence = await retrieve_guidelines(
        content.body,
        str(content.organisation_id),
    )
    return await generate_suggestions(
        SuggestionRequest(
            original_content=content.body,
            findings=report.findings,
            guideline_context=evidence,
        )
    )

