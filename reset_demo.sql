DELETE FROM product_orders;
DELETE FROM service_activations;
DELETE FROM audit_logs;
SELECT 'Reset Complete - Product Orders: ' || COUNT(*) FROM product_orders;
SELECT 'Reset Complete - Service Activations: ' || COUNT(*) FROM service_activations;
