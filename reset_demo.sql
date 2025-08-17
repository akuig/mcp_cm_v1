-- Delete demo data in correct order
DELETE FROM order_addresses;
DELETE FROM activation_addresses;
DELETE FROM orders;
DELETE FROM service_activations;
DELETE FROM sync_operations;

-- Verification
SELECT 'Reset Complete!' as status;
SELECT 'Orders: ' || COUNT(*) || ' remaining' as orders_status FROM orders;
SELECT 'Service Activations: ' || COUNT(*) || ' remaining' as activations_status FROM service_activations;
SELECT 'Customers: ' || COUNT(*) || ' preserved' as customers_status FROM customers;
SELECT 'Product Offerings: ' || COUNT(*) || ' preserved' as offerings_status FROM product_offerings;

