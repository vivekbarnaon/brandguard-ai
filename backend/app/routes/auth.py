from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies.auth import current_user, resolve_user_role
from app.models import OrganisationMember, User
from app.schemas.common import RoleResponse, UserProfileResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/me", response_model=UserProfileResponse)
@router.get("/profile", response_model=UserProfileResponse)
async def me(
    user: Annotated[User, Depends(current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    organisation_id: Optional[UUID] = None,
):
    role, _ = await resolve_user_role(user, db, organisation_id=organisation_id)
    all_members = await db.scalars(
        select(OrganisationMember).where(OrganisationMember.user_id == user.id)
    )
    roles_list = [
        {"organisation_id": str(m.organisation_id), "role": m.role.value}
        for m in all_members
    ]
    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "role": role.value,
        "roles": roles_list,
        "created_at": user.created_at,
    }


@router.get("/role", response_model=RoleResponse)
@router.get("/me/role", response_model=RoleResponse)
async def get_role(
    user: Annotated[User, Depends(current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    organisation_id: Optional[UUID] = None,
):
    role, _ = await resolve_user_role(user, db, organisation_id=organisation_id)
    all_members = await db.scalars(
        select(OrganisationMember).where(OrganisationMember.user_id == user.id)
    )
    roles_list = [
        {"organisation_id": str(m.organisation_id), "role": m.role.value}
        for m in all_members
    ]
    return {
        "role": role.value,
        "email": user.email,
        "roles": roles_list,
    }

