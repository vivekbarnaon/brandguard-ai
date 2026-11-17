from __future__ import annotations

import enum
import uuid
from datetime import datetime
from typing import Any, Optional

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, JSON, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, Timestamped


class Role(str, enum.Enum):
    ADMIN = "ADMIN"
    CREATOR = "CREATOR"
    MANAGER = "MANAGER"
    BRAND_REVIEWER = "BRAND_REVIEWER"


class ProcessingStatus(str, enum.Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    PROCESSED = "PROCESSED"
    FAILED = "FAILED"


class ContentStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    ANALYZED = "ANALYZED"
    SUBMITTED = "SUBMITTED"
    REVISION_REQUESTED = "REVISION_REQUESTED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class ApprovalDecision(str, enum.Enum):
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    REVISION_REQUESTED = "REVISION_REQUESTED"


class User(Timestamped, Base):
    __tablename__ = "users"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    email: Mapped[str] = mapped_column(String(320), nullable=False)
    name: Mapped[Optional[str]] = mapped_column(String(200))


class Organisation(Timestamped, Base):
    __tablename__ = "organisations"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    members: Mapped[list["OrganisationMember"]] = relationship(back_populates="organisation")


class OrganisationMember(Timestamped, Base):
    __tablename__ = "organisation_members"
    __table_args__ = (UniqueConstraint("organisation_id", "user_id"),)
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organisation_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organisations.id", ondelete="CASCADE"))
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    role: Mapped[Role] = mapped_column(Enum(Role, name="role"), nullable=False)
    organisation: Mapped[Organisation] = relationship(back_populates="members")


class Document(Timestamped, Base):
    __tablename__ = "documents"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organisation_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organisations.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    storage_path: Mapped[str] = mapped_column(String(500), nullable=False, unique=True)
    processing_status: Mapped[ProcessingStatus] = mapped_column(Enum(ProcessingStatus, name="processing_status"), default=ProcessingStatus.PENDING)
    uploaded_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))


class GuidelineChunk(Timestamped, Base):
    __tablename__ = "guideline_chunks"
    __table_args__ = (UniqueConstraint("document_id", "chunk_id"),)
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organisation_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organisations.id", ondelete="CASCADE"))
    document_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("documents.id", ondelete="CASCADE"))
    chunk_id: Mapped[str] = mapped_column(String(255), nullable=False)
    guideline_text: Mapped[str] = mapped_column(Text, nullable=False)
    page_number: Mapped[Optional[int]] = mapped_column(Integer)


class Content(Timestamped, Base):
    __tablename__ = "contents"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organisation_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organisations.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    created_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    status: Mapped[ContentStatus] = mapped_column(Enum(ContentStatus, name="content_status"), default=ContentStatus.DRAFT)
    version: Mapped[int] = mapped_column(Integer, default=1)


class ComplianceReport(Timestamped, Base):
    __tablename__ = "compliance_reports"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("contents.id", ondelete="CASCADE"))
    score: Mapped[float] = mapped_column(nullable=False)
    overall_status: Mapped[str] = mapped_column(String(50), nullable=False)
    findings: Mapped[list[dict[str, Any]]] = mapped_column(JSON, nullable=False)


class ApprovalRecord(Timestamped, Base):
    __tablename__ = "approval_records"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("contents.id", ondelete="CASCADE"))
    reviewer_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    decision: Mapped[ApprovalDecision] = mapped_column(Enum(ApprovalDecision, name="approval_decision"))
    comments: Mapped[Optional[str]] = mapped_column(Text)


class AuditLog(Timestamped, Base):
    __tablename__ = "audit_logs"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organisation_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organisations.id", ondelete="CASCADE"))
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True))
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

