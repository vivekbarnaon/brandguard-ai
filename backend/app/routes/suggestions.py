from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.database import get_db
from app.dependencies.auth import current_user
from app.models import Content, User
from app.routes.content import get_content
from app.services.aiml import call_aiml

router = APIRouter(prefix="/suggestions", tags=["suggestions"])


@router.post("/generate")
async def generate(content_id: UUID, user: Annotated[User, Depends(current_user)], db: Annotated[AsyncSession, Depends(get_db)]):
    content = await get_content(content_id, db, user.id)
    return await call_aiml(get_settings().aiml_suggestions_path, {"content_id": str(content.id), "organisation_id": str(content.organisation_id), "content": content.body})

