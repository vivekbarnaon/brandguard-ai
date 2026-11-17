from typing import Annotated

from fastapi import APIRouter, Depends

from app.dependencies.auth import current_user
from app.models import User

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/me")
@router.get("/profile")
async def me(user: Annotated[User, Depends(current_user)]):
    return {"id": user.id, "email": user.email, "name": user.name, "created_at": user.created_at}

