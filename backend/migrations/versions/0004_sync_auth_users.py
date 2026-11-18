"""Synchronize Supabase authentication users with application users."""

from alembic import op


revision = "0004_sync_auth_users"
down_revision = "0003_audit_log_created_at"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        insert into public.users (id, email, name)
        select
            auth_user.id,
            coalesce(auth_user.email, ''),
            coalesce(auth_user.raw_user_meta_data->>'name',
                     auth_user.raw_user_meta_data->>'full_name')
        from auth.users as auth_user
        on conflict (id) do update
        set email = excluded.email,
            name = excluded.name
        """
    )
    op.execute(
        """
        create or replace function public.sync_brandguard_auth_user()
        returns trigger
        language plpgsql
        security definer
        set search_path = public
        as $function$
        begin
            insert into public.users (id, email, name)
            values (
                new.id,
                coalesce(new.email, ''),
                coalesce(new.raw_user_meta_data->>'name',
                         new.raw_user_meta_data->>'full_name')
            )
            on conflict (id) do update
            set email = excluded.email,
                name = excluded.name;
            return new;
        end;
        $function$
        """
    )
    op.execute(
        """
        create trigger sync_brandguard_auth_user
        after insert or update of email, raw_user_meta_data
        on auth.users
        for each row
        execute function public.sync_brandguard_auth_user()
        """
    )


def downgrade() -> None:
    op.execute("drop trigger if exists sync_brandguard_auth_user on auth.users")
    op.execute("drop function if exists public.sync_brandguard_auth_user()")
