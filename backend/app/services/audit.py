from __future__ import annotations

import uuid
from typing import Any
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import AuditLog


async def record(db: AsyncSession, organisation_id: uuid.UUID, user_id: uuid.UUID, action: str, entity_id: Optional[uuid.UUID] = None, metadata: Optional[dict[str, Any]] = None) -> None:
    db.add(AuditLog(organisation_id=organisation_id, user_id=user_id, action=action, entity_id=entity_id, metadata_json=metadata or {}))

