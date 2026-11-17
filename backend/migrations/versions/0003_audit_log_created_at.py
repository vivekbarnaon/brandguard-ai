"""Add created_at to audit logs.

Revision ID: 0003_audit_log_created_at
Revises: 0002_guideline_chunks
"""

from alembic import op
import sqlalchemy as sa


revision = "0003_audit_log_created_at"
down_revision = "0002_guideline_chunks"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "audit_logs",
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column("audit_logs", "created_at")
