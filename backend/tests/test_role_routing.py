import os
import uuid
import pytest
from unittest.mock import AsyncMock, MagicMock

os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://postgres:password@localhost:5432/postgres")
os.environ.setdefault("SUPABASE_URL", "https://example.supabase.co")
os.environ.setdefault("SUPABASE_PUBLISHABLE_KEY", "sb_publishable_test")
os.environ.setdefault("SUPABASE_SECRET_KEY", "sb_secret_test")

from app.dependencies.auth import resolve_user_role, require_roles
from app.models import OrganisationMember, Role, User
from app.main import app
from app.dependencies.auth import current_user
from app.core.database import get_db
from fastapi.testclient import TestClient


@pytest.mark.asyncio
async def test_resolve_user_role_defaults_to_admin():
    # User with no memberships
    mock_db = MagicMock()
    mock_db.scalars = AsyncMock(return_value=[])

    user = User(id=uuid.uuid4(), email="newuser@example.com", name="New User")
    role, members = await resolve_user_role(user, mock_db)

    assert role == Role.ADMIN
    assert members == []


@pytest.mark.asyncio
async def test_resolve_user_role_preserves_assigned_role():
    user = User(id=uuid.uuid4(), email="creator@example.com", name="Creator User")
    org_id = uuid.uuid4()
    member = OrganisationMember(
        id=uuid.uuid4(),
        organisation_id=org_id,
        user_id=user.id,
        role=Role.CREATOR,
    )

    mock_db = MagicMock()
    mock_db.scalars = AsyncMock(return_value=[member])
    mock_db.scalar = AsyncMock(return_value=member)

    # When query without org_id
    role, members = await resolve_user_role(user, mock_db)
    assert role == Role.CREATOR
    assert len(members) == 1

    # When query with org_id
    role_with_org, members_with_org = await resolve_user_role(user, mock_db, organisation_id=org_id)
    assert role_with_org == Role.CREATOR
    assert len(members_with_org) == 1


@pytest.mark.asyncio
async def test_resolve_user_role_admin_precedence():
    user = User(id=uuid.uuid4(), email="multirole@example.com", name="Multi Role")
    m1 = OrganisationMember(id=uuid.uuid4(), organisation_id=uuid.uuid4(), user_id=user.id, role=Role.CREATOR)
    m2 = OrganisationMember(id=uuid.uuid4(), organisation_id=uuid.uuid4(), user_id=user.id, role=Role.ADMIN)

    mock_db = MagicMock()
    mock_db.scalars = AsyncMock(return_value=[m1, m2])

    role, members = await resolve_user_role(user, mock_db)
    assert role == Role.ADMIN
    assert len(members) == 2


def test_auth_me_and_role_endpoints():
    test_user = User(id=uuid.uuid4(), email="testadmin@example.com", name="Test Admin")

    async def override_current_user():
        return test_user

    async def override_get_db():
        mock_session = MagicMock()
        mock_session.scalars = AsyncMock(return_value=[])
        mock_session.scalar = AsyncMock(return_value=None)
        yield mock_session

    app.dependency_overrides[current_user] = override_current_user
    app.dependency_overrides[get_db] = override_get_db

    client = TestClient(app)

    try:
        # Test /api/v1/auth/me
        res = client.get("/api/v1/auth/me")
        assert res.status_code == 200
        data = res.json()
        assert data["email"] == "testadmin@example.com"
        assert data["role"] == "ADMIN"
        assert "roles" in data

        # Test /api/v1/auth/profile
        res_profile = client.get("/api/v1/auth/profile")
        assert res_profile.status_code == 200
        assert res_profile.json()["role"] == "ADMIN"

        # Test /api/v1/auth/role
        res_role = client.get("/api/v1/auth/role")
        assert res_role.status_code == 200
        role_data = res_role.json()
        assert role_data["role"] == "ADMIN"
        assert role_data["email"] == "testadmin@example.com"

        # Test /api/v1/auth/me/role
        res_me_role = client.get("/api/v1/auth/me/role")
        assert res_me_role.status_code == 200
        assert res_me_role.json()["role"] == "ADMIN"
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_require_roles_allows_admin():
    test_user = User(id=uuid.uuid4(), email="admin@example.com", name="Admin")
    org_id = uuid.uuid4()
    admin_member = OrganisationMember(id=uuid.uuid4(), organisation_id=org_id, user_id=test_user.id, role=Role.ADMIN)

    mock_db = MagicMock()
    mock_db.scalar = AsyncMock(return_value=admin_member)

    dependency = require_roles(Role.CREATOR)
    result = await dependency(user=test_user, organisation_id=org_id, db=mock_db)
    assert result.role == Role.ADMIN


@pytest.mark.asyncio
async def test_require_roles_unassigned_treated_as_admin():
    test_user = User(id=uuid.uuid4(), email="unassigned@example.com", name="Unassigned")
    org_id = uuid.uuid4()

    mock_db = MagicMock()
    # First query returns None (not yet in org)
    mock_db.scalar = AsyncMock(return_value=None)
    mock_db.add = MagicMock()
    mock_db.commit = AsyncMock()
    mock_db.refresh = AsyncMock()

    dependency = require_roles(Role.CREATOR)
    result = await dependency(user=test_user, organisation_id=org_id, db=mock_db)
    assert result.role == Role.ADMIN


@pytest.mark.asyncio
async def test_require_roles_denies_wrong_role():
    from fastapi import HTTPException
    test_user = User(id=uuid.uuid4(), email="creator@example.com", name="Creator")
    org_id = uuid.uuid4()
    creator_member = OrganisationMember(id=uuid.uuid4(), organisation_id=org_id, user_id=test_user.id, role=Role.CREATOR)

    mock_db = MagicMock()
    mock_db.scalar = AsyncMock(return_value=creator_member)

    dependency = require_roles(Role.MANAGER)
    with pytest.raises(HTTPException) as exc_info:
        await dependency(user=test_user, organisation_id=org_id, db=mock_db)
    assert exc_info.value.status_code == 403
