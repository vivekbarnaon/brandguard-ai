from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies.auth import membership
from app.models import ComplianceReport, Content, ContentStatus, Document, OrganisationMember

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/{organisation_id}")
async def dashboard(organisation_id: UUID, _: Annotated[OrganisationMember, Depends(membership)], db: Annotated[AsyncSession, Depends(get_db)]):
    documents = await db.scalar(select(func.count(Document.id)).where(Document.organisation_id == organisation_id))
    content = await db.scalar(select(func.count(Content.id)).where(Content.organisation_id == organisation_id))
    reports = await db.scalar(select(func.count(ComplianceReport.id)).join(Content).where(Content.organisation_id == organisation_id))
    average = await db.scalar(select(func.avg(ComplianceReport.score)).join(Content).where(Content.organisation_id == organisation_id))
    pending = await db.scalar(select(func.count(Content.id)).where(Content.organisation_id == organisation_id, Content.status == ContentStatus.SUBMITTED))
    return {"documents": documents or 0, "content": content or 0, "reports": reports or 0, "average_score": average, "pending_approvals": pending or 0}

