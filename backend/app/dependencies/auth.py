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
        user = User(id=user_id, email=claims.get("email", ""), name=claims.get("user_metadata", {}).get("name"))
        db.add(user)
        await db.commit()
        await db.refresh(user)
    return user


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
        if member is None or (roles and member.role not in roles):
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

