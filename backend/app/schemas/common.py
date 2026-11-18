from __future__ import annotations

from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class OrganisationCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)


class OrganisationResponse(ORMModel):
    id: UUID
    name: str
    created_at: datetime


class OrganisationMemberCreate(BaseModel):
    email: str = Field(min_length=3, max_length=320)
    role: str


class OrganisationMemberRoleUpdate(BaseModel):
    role: str


class OrganisationMemberResponse(ORMModel):
    id: UUID
    user_id: UUID
    email: str
    name: Optional[str] = None
    role: str


class UserProfileResponse(ORMModel):
    id: UUID
    email: str
    name: Optional[str] = None
    role: str = "ADMIN"
    roles: list[dict[str, Any]] = []
    created_at: Optional[datetime] = None


class RoleResponse(BaseModel):
    role: str = "ADMIN"
    email: str
    roles: list[dict[str, Any]] = []


class ContentCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    body: str = Field(min_length=1)


class ContentUpdate(ContentCreate):
    pass


class ContentResponse(ORMModel):
    id: UUID
    organisation_id: UUID
    title: str
    body: str
    status: str
    version: int
    created_at: datetime


class ApprovalRequest(BaseModel):
    decision: str
    comments: Optional[str] = None

