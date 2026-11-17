from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies.auth import current_user, require_roles
from app.models import ApprovalDecision, ApprovalRecord, Content, ContentStatus, OrganisationMember, Role, User
from app.schemas.common import ApprovalRequest
from app.services.audit import record

router = APIRouter(prefix="/approvals", tags=["approvals"])


@router.post("/{content_id}/submit")
async def submit(content_id: UUID, user: Annotated[User, Depends(current_user)], db: Annotated[AsyncSession, Depends(get_db)]):
    content = await db.get(Content, content_id)
    if content is None or await db.scalar(select(OrganisationMember).where(OrganisationMember.organisation_id == content.organisation_id, OrganisationMember.user_id == user.id)) is None:
        raise HTTPException(status_code=404, detail="Content not found")
    content.status = ContentStatus.SUBMITTED
    await record(db, content.organisation_id, user.id, "content.submitted", content.id)
    await db.commit()
    return content


@router.post("/{content_id}/review")
async def review(content_id: UUID, payload: ApprovalRequest, user: Annotated[User, Depends(current_user)], db: Annotated[AsyncSession, Depends(get_db)]):
    if payload.decision not in ApprovalDecision._value2member_map_:
        raise HTTPException(status_code=422, detail="Invalid approval decision")
    content = await db.get(Content, content_id)
    if content is None:
        raise HTTPException(status_code=404, detail="Content not found")
    member = await db.scalar(select(OrganisationMember).where(OrganisationMember.organisation_id == content.organisation_id, OrganisationMember.user_id == user.id))
    if member is None or member.role not in {Role.ADMIN, Role.MANAGER, Role.BRAND_REVIEWER}:
        raise HTTPException(status_code=403, detail="Only authorised reviewers can review content")
    decision = ApprovalDecision(payload.decision)
    content.status = ContentStatus(decision.value)
    approval = ApprovalRecord(content_id=content.id, reviewer_id=user.id, decision=decision, comments=payload.comments)
    db.add(approval)
    await record(db, content.organisation_id, user.id, f"content.reviewed.{decision.value.lower()}", content.id)
    await db.commit()
    return approval


@router.get("/pending")
async def pending(organisation_id: UUID, _: Annotated[OrganisationMember, Depends(require_roles(Role.ADMIN, Role.MANAGER, Role.BRAND_REVIEWER))], db: Annotated[AsyncSession, Depends(get_db)]):
    return list(await db.scalars(select(Content).where(Content.organisation_id == organisation_id, Content.status == ContentStatus.SUBMITTED)))


@router.get("/{content_id}/history")
async def history(content_id: UUID, user: Annotated[User, Depends(current_user)], db: Annotated[AsyncSession, Depends(get_db)]):
    content = await db.get(Content, content_id)
    if content is None or await db.scalar(select(OrganisationMember).where(OrganisationMember.organisation_id == content.organisation_id, OrganisationMember.user_id == user.id)) is None:
        raise HTTPException(status_code=404, detail="Content not found")
    return list(await db.scalars(select(ApprovalRecord).where(ApprovalRecord.content_id == content_id).order_by(ApprovalRecord.created_at.desc())))

