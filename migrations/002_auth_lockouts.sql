

BEGIN;

DO $$
BEGIN
    IF to_regclass('public.users') IS NULL THEN
        RAISE EXCEPTION 'Expected users table was not found. Check DATABASE_URL before migrating.';
    END IF;
END
$$;

ALTER TABLE users
    ADD COLUMN IF NOT EXISTS failed_login_attempts INTEGER NOT NULL DEFAULT 0,
    ADD COLUMN IF NOT EXISTS locked_until TIMESTAMPTZ NULL,
    ADD COLUMN IF NOT EXISTS failed_mfa_attempts INTEGER NOT NULL DEFAULT 0,
    ADD COLUMN IF NOT EXISTS mfa_locked_until TIMESTAMPTZ NULL;

COMMIT;
