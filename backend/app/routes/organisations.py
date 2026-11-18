from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies.auth import current_user, membership
from app.models import Organisation, OrganisationMember, Role, User
from app.schemas.common import (
    OrganisationCreate,
    OrganisationMemberCreate,
    OrganisationMemberRoleUpdate,
    OrganisationResponse,
)

router = APIRouter(prefix="/organisations", tags=["organisations"])


async def require_admin_member(
    organisation_id: UUID,
    user: User,
    db: AsyncSession,
) -> OrganisationMember:
    member = await db.scalar(
        select(OrganisationMember).where(
            OrganisationMember.organisation_id == organisation_id,
            OrganisationMember.user_id == user.id,
        )
    )
    if member is None or member.role != Role.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient organisation permissions",
        )
    return member


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


@router.get("/{organisation_id}/membership")
async def get_membership(
    organisation_id: UUID,
    user: Annotated[User, Depends(current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    member = await db.scalar(
        select(OrganisationMember).where(
            OrganisationMember.organisation_id == organisation_id,
            OrganisationMember.user_id == user.id,
        )
    )
    if member is None:
        raise HTTPException(status_code=403, detail="Organisation access denied")
    return {"role": member.role.value}


@router.get("/{organisation_id}/members")
async def list_members(
    organisation_id: UUID,
    user: Annotated[User, Depends(current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    await require_admin_member(organisation_id, user, db)
    rows = await db.execute(
        select(OrganisationMember, User)
        .join(User, User.id == OrganisationMember.user_id)
        .where(OrganisationMember.organisation_id == organisation_id)
        .order_by(User.email)
    )
    return [
        {
            "id": member.id,
            "user_id": member.user_id,
            "email": user.email,
            "name": user.name,
            "role": member.role.value,
        }
        for member, user in rows.all()
    ]


@router.post("/{organisation_id}/members", status_code=status.HTTP_201_CREATED)
async def add_member(
    organisation_id: UUID,
    payload: OrganisationMemberCreate,
    user: Annotated[User, Depends(current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    await require_admin_member(organisation_id, user, db)
    try:
        role = Role(payload.role)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail="Invalid organisation role") from exc

    user = await db.scalar(
        select(User).where(
            User.email.ilike(payload.email.strip())
        )
    )
    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User must sign up before they can be added",
        )

    existing = await db.scalar(
        select(OrganisationMember).where(
            OrganisationMember.organisation_id == organisation_id,
            OrganisationMember.user_id == user.id,
        )
    )
    if existing is not None:
        raise HTTPException(status_code=409, detail="User is already a member")

    member = OrganisationMember(
        organisation_id=organisation_id,
        user_id=user.id,
        role=role,
    )
    db.add(member)
    await db.commit()
    await db.refresh(member)
    return {
        "id": member.id,
        "user_id": member.user_id,
        "email": user.email,
        "name": user.name,
        "role": member.role.value,
    }


@router.patch("/{organisation_id}/members/{member_id}")
async def update_member_role(
    organisation_id: UUID,
    member_id: UUID,
    payload: OrganisationMemberRoleUpdate,
    user: Annotated[User, Depends(current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    await require_admin_member(organisation_id, user, db)
    try:
        role = Role(payload.role)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail="Invalid organisation role") from exc

    member = await db.get(OrganisationMember, member_id)
    if member is None or member.organisation_id != organisation_id:
        raise HTTPException(status_code=404, detail="Member not found")
    member.role = role
    await db.commit()
    await db.refresh(member)
    user = await db.get(User, member.user_id)
    return {
        "id": member.id,
        "user_id": member.user_id,
        "email": user.email if user else "",
        "name": user.name if user else None,
        "role": member.role.value,
    }

