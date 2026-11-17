from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies.auth import current_user
from app.models import ComplianceReport, Content, OrganisationMember, User
from app.schemas.aiml import ComplianceRequest
from app.services import aiml
from app.services.audit import record

router = APIRouter(prefix="/compliance", tags=["compliance"])


@router.post("/analyze")
async def analyze(content_id: UUID, user: Annotated[User, Depends(current_user)], db: Annotated[AsyncSession, Depends(get_db)]):
    content = await db.get(Content, content_id)
    if content is None or await db.scalar(select(OrganisationMember).where(OrganisationMember.organisation_id == content.organisation_id, OrganisationMember.user_id == user.id)) is None:
        raise HTTPException(status_code=404, detail="Content not found")
    evidence = await aiml.retrieve_guidelines(
        content.body,
        str(content.organisation_id),
    )
    result = await aiml.analyze(
        ComplianceRequest(
            content_id=str(content.id),
            organisation_id=str(content.organisation_id),
            original_content=content.body,
            guideline_context=evidence,
        )
    )
    try:
        report = ComplianceReport(content_id=content.id, score=result.compliance_score, overall_status=result.overall_status, findings=result.findings)
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=502, detail="AI/ML response failed compliance schema validation") from exc
    db.add(report)
    await record(db, content.organisation_id, user.id, "compliance.analyzed", report.id)
    await db.commit()
    await db.refresh(report)
    return report


@router.get("/reports")
async def reports(organisation_id: UUID, user: Annotated[User, Depends(current_user)], db: Annotated[AsyncSession, Depends(get_db)]):
    if await db.scalar(select(OrganisationMember).where(OrganisationMember.organisation_id == organisation_id, OrganisationMember.user_id == user.id)) is None:
        raise HTTPException(status_code=403, detail="Organisation access denied")
    return list(await db.scalars(select(ComplianceReport).join(Content).where(Content.organisation_id == organisation_id).order_by(ComplianceReport.created_at.desc())))


@router.get("/reports/{report_id}")
async def report(report_id: UUID, user: Annotated[User, Depends(current_user)], db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.scalar(select(ComplianceReport).join(Content).where(ComplianceReport.id == report_id))
    if result is None or await db.scalar(select(OrganisationMember).where(OrganisationMember.organisation_id == (await db.get(Content, result.content_id)).organisation_id, OrganisationMember.user_id == user.id)) is None:
        raise HTTPException(status_code=404, detail="Report not found")
    return result

