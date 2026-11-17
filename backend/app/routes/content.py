from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies.auth import current_user, membership
from app.models import Content, ContentStatus, OrganisationMember, User
from app.schemas.common import ContentCreate, ContentResponse, ContentUpdate
from app.services.audit import record

router = APIRouter(prefix="/content", tags=["content"])


async def get_content(content_id: UUID, db: AsyncSession, user_id: UUID) -> Content:
    result = await db.scalar(select(Content).where(Content.id == content_id))
    if result is None:
        raise HTTPException(status_code=404, detail="Content not found")
    member = await db.scalar(select(OrganisationMember).where(OrganisationMember.organisation_id == result.organisation_id, OrganisationMember.user_id == user_id))
    if member is None:
        raise HTTPException(status_code=403, detail="Content is outside your organisation")
    return result


@router.post("", response_model=ContentResponse, status_code=status.HTTP_201_CREATED)
async def create_content(payload: ContentCreate, organisation_id: UUID, user: Annotated[User, Depends(current_user)], _: Annotated[OrganisationMember, Depends(membership)], db: Annotated[AsyncSession, Depends(get_db)]):
    content = Content(organisation_id=organisation_id, title=payload.title, body=payload.body, created_by=user.id)
    db.add(content)
    await record(db, organisation_id, user.id, "content.created", content.id)
    await db.commit()
    await db.refresh(content)
    return content


@router.get("", response_model=list[ContentResponse])
async def list_content(organisation_id: UUID, _: Annotated[OrganisationMember, Depends(membership)], db: Annotated[AsyncSession, Depends(get_db)]):
    return list(await db.scalars(select(Content).where(Content.organisation_id == organisation_id).order_by(Content.created_at.desc())))


@router.get("/{content_id}", response_model=ContentResponse)
async def read_content(content_id: UUID, user: Annotated[User, Depends(current_user)], db: Annotated[AsyncSession, Depends(get_db)]):
    return await get_content(content_id, db, user.id)


@router.put("/{content_id}", response_model=ContentResponse)
async def update_content(content_id: UUID, payload: ContentUpdate, user: Annotated[User, Depends(current_user)], db: Annotated[AsyncSession, Depends(get_db)]):
    content = await get_content(content_id, db, user.id)
    content.title, content.body, content.version = payload.title, payload.body, content.version + 1
    content.status = ContentStatus.DRAFT
    await record(db, content.organisation_id, user.id, "content.updated", content.id, {"version": content.version})
    await db.commit()
    await db.refresh(content)
    return content

