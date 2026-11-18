from __future__ import annotations

import uuid
from typing import Annotated, Any, Optional

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.config import get_settings
from app.core.security import verify_token
from app.models import OrganisationMember, Role, User

bearer = HTTPBearer(auto_error=True)


async def current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    claims = verify_token(credentials.credentials)
    try:
        user_id = uuid.UUID(claims["sub"])
    except (KeyError, ValueError) as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has no valid user subject") from exc
    user = await db.get(User, user_id)
    if user is None:
        email = claims.get("email", "")
        name = claims.get("user_metadata", {}).get("name")
        if email:
            existing = await db.scalar(select(User).where(User.email.ilike(email.strip())))
            if existing is not None and existing.id != user_id:
                old_id = existing.id
                user = User(id=user_id, email=email, name=name or existing.name)
                db.add(user)
                await db.flush()
                # Reassign any memberships linked to placeholder user
                members = list(await db.scalars(select(OrganisationMember).where(OrganisationMember.user_id == old_id)))
                for m in members:
                    m.user_id = user_id
                await db.delete(existing)
                await db.commit()
                await db.refresh(user)
                return user
        user = User(id=user_id, email=email, name=name)
        db.add(user)
        await db.commit()
        await db.refresh(user)
    return user


async def resolve_user_role(
    user: User,
    db: AsyncSession,
    organisation_id: Optional[uuid.UUID] = None,
) -> tuple[Role, list[OrganisationMember]]:
    """
    Resolve the role for a user / email.
    If there is not any role related to the email, treat that as ADMIN.
    """
    if organisation_id is not None:
        member = await db.scalar(
            select(OrganisationMember).where(
                OrganisationMember.organisation_id == organisation_id,
                OrganisationMember.user_id == user.id,
            )
        )
        if member is not None:
            return member.role, [member]
        # In this organisation, no role is related to this email -> treat as ADMIN
        return Role.ADMIN, []

    # Overall / global role
    members = list(
        await db.scalars(
            select(OrganisationMember).where(OrganisationMember.user_id == user.id)
        )
    )
    if members:
        for m in members:
            if m.role == Role.ADMIN:
                return Role.ADMIN, members
        return members[0].role, members

    # If not any role is related to the email, treat as ADMIN
    return Role.ADMIN, []


def require_roles(*roles: Role):
    async def dependency(
        user: Annotated[User, Depends(current_user)],
        organisation_id: uuid.UUID,
        db: Annotated[AsyncSession, Depends(get_db)],
    ) -> OrganisationMember:
        member = await db.scalar(
            select(OrganisationMember).where(
                OrganisationMember.organisation_id == organisation_id,
                OrganisationMember.user_id == user.id,
            )
        )
        if member is None:
            # If not any role is related to the email, treat that as admin
            member = OrganisationMember(
                organisation_id=organisation_id,
                user_id=user.id,
                role=Role.ADMIN,
            )
            db.add(member)
            try:
                await db.commit()
                await db.refresh(member)
            except Exception:
                await db.rollback()
                member = await db.scalar(
                    select(OrganisationMember).where(
                        OrganisationMember.organisation_id == organisation_id,
                        OrganisationMember.user_id == user.id,
                    )
                )

        if member is None:
            member = OrganisationMember(
                organisation_id=organisation_id,
                user_id=user.id,
                role=Role.ADMIN,
            )

        if roles and member.role not in roles and member.role != Role.ADMIN:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient organisation permissions")
        return member

    return dependency


async def membership(
    organisation_id: uuid.UUID,
    user: Annotated[User, Depends(current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> OrganisationMember:
    return await require_roles()(organisation_id=organisation_id, user=user, db=db)


async def internal_aiml(x_aiml_internal_token: Annotated[Optional[str], Header()] = None) -> None:
    configured = get_settings().aiml_internal_token
    if configured is None or x_aiml_internal_token != configured.get_secret_value():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="AIML internal access denied")

