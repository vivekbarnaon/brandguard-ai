"""Store organisation-scoped processed guideline evidence."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0002_guideline_chunks"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade():
    uuid = postgresql.UUID(as_uuid=True)
    op.create_table(
        "guideline_chunks",
        sa.Column("id", uuid, primary_key=True),
        sa.Column("organisation_id", uuid, sa.ForeignKey("organisations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("document_id", uuid, sa.ForeignKey("documents.id", ondelete="CASCADE"), nullable=False),
        sa.Column("chunk_id", sa.String(255), nullable=False),
        sa.Column("guideline_text", sa.Text, nullable=False),
        sa.Column("page_number", sa.Integer),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("document_id", "chunk_id"),
    )
    op.create_index("ix_guideline_chunks_organisation_id", "guideline_chunks", ["organisation_id"])


def downgrade():
    op.drop_index("ix_guideline_chunks_organisation_id", table_name="guideline_chunks")
    op.drop_table("guideline_chunks")
