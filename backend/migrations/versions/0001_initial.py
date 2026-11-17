"""Create BrandGuard data model and private storage policies."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    role = postgresql.ENUM("ADMIN", "CREATOR", "MANAGER", "BRAND_REVIEWER", name="role")
    processing = postgresql.ENUM("PENDING", "PROCESSING", "PROCESSED", "FAILED", name="processing_status")
    content_status = postgresql.ENUM("DRAFT", "ANALYZED", "SUBMITTED", "REVISION_REQUESTED", "APPROVED", "REJECTED", name="content_status")
    decision = postgresql.ENUM("APPROVED", "REJECTED", "REVISION_REQUESTED", name="approval_decision")
    for enum in (role, processing, content_status, decision):
        enum.create(op.get_bind(), checkfirst=True)
    uuid = postgresql.UUID(as_uuid=True)
    op.create_table("users", sa.Column("id", uuid, primary_key=True), sa.Column("email", sa.String(320), nullable=False), sa.Column("name", sa.String(200)), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
    op.create_table("organisations", sa.Column("id", uuid, primary_key=True), sa.Column("name", sa.String(200), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
    op.create_table("organisation_members", sa.Column("id", uuid, primary_key=True), sa.Column("organisation_id", uuid, sa.ForeignKey("organisations.id", ondelete="CASCADE")), sa.Column("user_id", uuid, sa.ForeignKey("users.id", ondelete="CASCADE")), sa.Column("role", role, nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False), sa.UniqueConstraint("organisation_id", "user_id"))
    op.create_table("documents", sa.Column("id", uuid, primary_key=True), sa.Column("organisation_id", uuid, sa.ForeignKey("organisations.id", ondelete="CASCADE")), sa.Column("name", sa.String(255), nullable=False), sa.Column("storage_path", sa.String(500), unique=True, nullable=False), sa.Column("processing_status", processing, nullable=False), sa.Column("uploaded_by", uuid, sa.ForeignKey("users.id")), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
    op.create_table("contents", sa.Column("id", uuid, primary_key=True), sa.Column("organisation_id", uuid, sa.ForeignKey("organisations.id", ondelete="CASCADE")), sa.Column("title", sa.String(255), nullable=False), sa.Column("body", sa.Text, nullable=False), sa.Column("created_by", uuid, sa.ForeignKey("users.id")), sa.Column("status", content_status, nullable=False), sa.Column("version", sa.Integer, nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
    op.create_table("compliance_reports", sa.Column("id", uuid, primary_key=True), sa.Column("content_id", uuid, sa.ForeignKey("contents.id", ondelete="CASCADE")), sa.Column("score", sa.Float, nullable=False), sa.Column("overall_status", sa.String(50), nullable=False), sa.Column("findings", postgresql.JSONB, nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
    op.create_table("approval_records", sa.Column("id", uuid, primary_key=True), sa.Column("content_id", uuid, sa.ForeignKey("contents.id", ondelete="CASCADE")), sa.Column("reviewer_id", uuid, sa.ForeignKey("users.id")), sa.Column("decision", decision, nullable=False), sa.Column("comments", sa.Text), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
    op.create_table("audit_logs", sa.Column("id", uuid, primary_key=True), sa.Column("organisation_id", uuid, sa.ForeignKey("organisations.id", ondelete="CASCADE")), sa.Column("user_id", uuid, sa.ForeignKey("users.id")), sa.Column("action", sa.String(100), nullable=False), sa.Column("entity_id", uuid), sa.Column("metadata_json", postgresql.JSONB, nullable=False), sa.Column("timestamp", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
    op.execute("insert into storage.buckets (id, name, public) values ('brand-guidelines', 'brand-guidelines', false) on conflict (id) do update set public = false")
    op.execute("""create policy "organisation members can read guidelines" on storage.objects for select to authenticated using (bucket_id = 'brand-guidelines' and exists (select 1 from public.organisation_members m where m.user_id = auth.uid() and m.organisation_id::text = (storage.foldername(name))[1]))""")
    op.execute("""create policy "creators can upload guidelines" on storage.objects for insert to authenticated with check (bucket_id = 'brand-guidelines' and exists (select 1 from public.organisation_members m where m.user_id = auth.uid() and m.role in ('ADMIN','CREATOR') and m.organisation_id::text = (storage.foldername(name))[1]))""")
    op.execute("""create policy "admins can delete guidelines" on storage.objects for delete to authenticated using (bucket_id = 'brand-guidelines' and exists (select 1 from public.organisation_members m where m.user_id = auth.uid() and m.role = 'ADMIN' and m.organisation_id::text = (storage.foldername(name))[1]))""")


def downgrade():
    op.execute("drop policy if exists \"admins can delete guidelines\" on storage.objects")
    op.execute("drop policy if exists \"creators can upload guidelines\" on storage.objects")
    op.execute("drop policy if exists \"organisation members can read guidelines\" on storage.objects")
    for table in ("audit_logs", "approval_records", "compliance_reports", "contents", "documents", "organisation_members", "organisations", "users"):
        op.drop_table(table)
    for name in ("approval_decision", "content_status", "processing_status", "role"):
        sa.Enum(name=name).drop(op.get_bind(), checkfirst=True)

