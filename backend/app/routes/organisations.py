from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies.auth import current_user, membership
from app.models import Organisation, OrganisationMember, Role, User
from app.schemas.common import OrganisationCreate, OrganisationResponse

router = APIRouter(prefix="/organisations", tags=["organisations"])


@router.post("", response_model=OrganisationResponse, status_code=status.HTTP_201_CREATED)
async def create_organisation(payload: OrganisationCreate, user: Annotated[User, Depends(current_user)], db: Annotated[AsyncSession, Depends(get_db)]):
    organisation = Organisation(name=payload.name)
    db.add(organisation)
    await db.flush()
    db.add(OrganisationMember(organisation_id=organisation.id, user_id=user.id, role=Role.ADMIN))
    await db.commit()
    await db.refresh(organisation)
    return organisation


@router.get("", response_model=list[OrganisationResponse])
async def list_organisations(user: Annotated[User, Depends(current_user)], db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.scalars(select(Organisation).join(OrganisationMember).where(OrganisationMember.user_id == user.id))
    return list(result)


@router.get("/{organisation_id}", response_model=OrganisationResponse)
async def get_organisation(organisation_id: UUID, db: Annotated[AsyncSession, Depends(get_db)], _: Annotated[OrganisationMember, Depends(membership)]):
    return await db.get(Organisation, organisation_id)

