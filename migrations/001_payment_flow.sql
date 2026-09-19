

BEGIN;

CREATE EXTENSION IF NOT EXISTS pgcrypto;

DO $$
BEGIN
    IF to_regclass('public.products') IS NULL
       OR to_regclass('public.sales') IS NULL
       OR to_regclass('public.payments') IS NULL THEN
        RAISE EXCEPTION 'Expected products, sales, and payments tables were not found. Check DATABASE_URL before migrating.';
    END IF;
END
$$;


ALTER TABLE products
    ADD COLUMN IF NOT EXISTS reserved_quantity NUMERIC(12, 2) NOT NULL DEFAULT 0;

ALTER TABLE sales
    ADD COLUMN IF NOT EXISTS sale_status VARCHAR(30);

UPDATE sales
SET sale_status = 'completed'
WHERE sale_status IS NULL OR BTRIM(sale_status) = '';

ALTER TABLE sales
    ALTER COLUMN sale_status SET DEFAULT 'pending',
    ALTER COLUMN sale_status SET NOT NULL;

ALTER TABLE sales
    ADD COLUMN IF NOT EXISTS public_status_token VARCHAR(64);

UPDATE sales
SET public_status_token = encode(gen_random_bytes(24), 'hex')
WHERE public_status_token IS NULL OR public_status_token = '';

DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM sales
        GROUP BY public_status_token
        HAVING COUNT(*) > 1
    ) THEN
        RAISE EXCEPTION 'Duplicate sales.public_status_token values exist; resolve them before creating the unique index.';
    END IF;
END
$$;

ALTER TABLE sales
    ALTER COLUMN public_status_token SET NOT NULL;

CREATE UNIQUE INDEX IF NOT EXISTS ix_sales_public_status_token
    ON sales (public_status_token);
.
ALTER TABLE payments
    ADD COLUMN IF NOT EXISTS payment_status VARCHAR(30);

UPDATE payments
SET payment_status = 'completed'
WHERE payment_status IS NULL OR BTRIM(payment_status) = '';

ALTER TABLE payments
    ALTER COLUMN payment_status SET DEFAULT 'pending',
    ALTER COLUMN payment_status SET NOT NULL;

ALTER TABLE payments ADD COLUMN IF NOT EXISTS payer_phone VARCHAR(20);
ALTER TABLE payments ADD COLUMN IF NOT EXISTS provider_reference VARCHAR(100);
ALTER TABLE payments ADD COLUMN IF NOT EXISTS provider_transaction_id VARCHAR(100);
ALTER TABLE payments ADD COLUMN IF NOT EXISTS provider_status VARCHAR(50);
ALTER TABLE payments ADD COLUMN IF NOT EXISTS idempotency_key VARCHAR(100);
ALTER TABLE payments ADD COLUMN IF NOT EXISTS status_message TEXT;
ALTER TABLE payments ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW();

DO $$
BEGIN
    IF EXISTS (
        SELECT idempotency_key
        FROM payments
        WHERE idempotency_key IS NOT NULL
        GROUP BY idempotency_key
        HAVING COUNT(*) > 1
    ) THEN
        RAISE EXCEPTION 'Duplicate payments.idempotency_key values exist; resolve them before creating the unique index.';
    END IF;

    IF EXISTS (
        SELECT provider_reference
        FROM payments
        WHERE provider_reference IS NOT NULL
        GROUP BY provider_reference
        HAVING COUNT(*) > 1
    ) THEN
        RAISE EXCEPTION 'Duplicate payments.provider_reference values exist; resolve them before creating the unique index.';
    END IF;
END
$$;

CREATE UNIQUE INDEX IF NOT EXISTS uq_payments_idempotency_key
    ON payments (idempotency_key)
    WHERE idempotency_key IS NOT NULL;

CREATE UNIQUE INDEX IF NOT EXISTS uq_payments_provider_reference
    ON payments (provider_reference)
    WHERE provider_reference IS NOT NULL;

COMMIT;
