-- Migration 001: Add missing FK constraints on orders.product_offering_id
-- and service_activations.service_specification_id.
--
-- Fails loudly if any existing rows would violate the new constraints,
-- rather than silently discarding data. Investigate and clean up
-- orphaned rows before re-running.
--
-- Idempotent: safe to re-run once the constraints exist.

\c telecom_catalog;

BEGIN;

-- 1. Pre-flight: detect orphaned rows.
DO $$
DECLARE
    orphan_orders INTEGER;
    orphan_activations INTEGER;
BEGIN
    SELECT COUNT(*) INTO orphan_orders
    FROM orders o
    WHERE o.product_offering_id IS NOT NULL
      AND NOT EXISTS (
        SELECT 1 FROM product_offerings po WHERE po.id = o.product_offering_id
      );

    SELECT COUNT(*) INTO orphan_activations
    FROM service_activations sa
    WHERE sa.service_specification_id IS NOT NULL
      AND NOT EXISTS (
        SELECT 1 FROM service_specifications ss WHERE ss.id = sa.service_specification_id
      );

    IF orphan_orders > 0 THEN
        RAISE EXCEPTION 'Aborting: % order(s) reference product_offering_id values that do not exist in product_offerings. Clean these up before applying this migration.', orphan_orders;
    END IF;

    IF orphan_activations > 0 THEN
        RAISE EXCEPTION 'Aborting: % service_activation(s) reference service_specification_id values that do not exist in service_specifications. Clean these up before applying this migration.', orphan_activations;
    END IF;
END $$;

-- 2. Add FK on orders.product_offering_id -> product_offerings.id
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'orders_product_offering_id_fkey'
    ) THEN
        ALTER TABLE orders
            ADD CONSTRAINT orders_product_offering_id_fkey
            FOREIGN KEY (product_offering_id) REFERENCES product_offerings(id);
    END IF;
END $$;

-- 3. Add FK on service_activations.service_specification_id -> service_specifications.id
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'service_activations_service_specification_id_fkey'
    ) THEN
        ALTER TABLE service_activations
            ADD CONSTRAINT service_activations_service_specification_id_fkey
            FOREIGN KEY (service_specification_id) REFERENCES service_specifications(id);
    END IF;
END $$;

COMMIT;
