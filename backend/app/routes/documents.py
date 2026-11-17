import uuid
import logging
from pathlib import PurePosixPath
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
import httpx
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.database import get_db
from app.dependencies.auth import current_user, membership, require_roles
from app.models import Document, OrganisationMember, ProcessingStatus, Role, User
from app.services.audit import record
from app.services.storage import delete_private, upload_private

router = APIRouter(prefix="/documents", tags=["documents"])
logger = logging.getLogger(__name__)


@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_document(organisation_id: UUID, file: Annotated[UploadFile, File()], user: Annotated[User, Depends(current_user)], _: Annotated[OrganisationMember, Depends(require_roles(Role.ADMIN, Role.CREATOR))], db: Annotated[AsyncSession, Depends(get_db)]):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=415, detail="Only PDF files are accepted")
    data = await file.read()
    if len(data) > get_settings().max_upload_bytes:
        raise HTTPException(status_code=413, detail="File exceeds the configured size limit")
    document_id = uuid.uuid4()
    safe_name = PurePosixPath(file.filename or "guidelines.pdf").name
    path = f"{organisation_id}/{document_id}/{safe_name}"
    try:
        await upload_private(path, data, "application/pdf")
        document = Document(id=document_id, organisation_id=organisation_id, name=safe_name, storage_path=path, uploaded_by=user.id, processing_status=ProcessingStatus.PENDING)
        db.add(document)
        await record(db, organisation_id, user.id, "document.uploaded", document.id)
        await db.commit()
        return document
    except (httpx.HTTPError, SQLAlchemyError):
        try:
            await delete_private(path)
        except httpx.HTTPError:
            logger.exception("Failed to clean up storage object after document upload failure")
        raise


@router.get("")
async def list_documents(organisation_id: UUID, _: Annotated[OrganisationMember, Depends(membership)], db: Annotated[AsyncSession, Depends(get_db)]):
    return list(await db.scalars(select(Document).where(Document.organisation_id == organisation_id).order_by(Document.created_at.desc())))


@router.get("/{document_id}")
async def get_document(document_id: UUID, user: Annotated[User, Depends(current_user)], db: Annotated[AsyncSession, Depends(get_db)]):
    document = await db.get(Document, document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    member = await db.scalar(select(OrganisationMember).where(OrganisationMember.organisation_id == document.organisation_id, OrganisationMember.user_id == user.id))
    if member is None:
        raise HTTPException(status_code=403, detail="Document is outside your organisation")
    return document


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_document(document_id: UUID, user: Annotated[User, Depends(current_user)], db: Annotated[AsyncSession, Depends(get_db)]):
    document = await get_document(document_id, user, db)
    await delete_private(document.storage_path)
    await db.delete(document)
    await db.commit()

