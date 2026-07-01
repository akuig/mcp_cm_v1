-- ================================================================
-- ADD BUSINESS PRODUCT TO SERVER 1 (MCP Local)
-- Backport enterprise offering from Server 2
-- ================================================================
-- Database: telecom_catalog
-- Execute with: psql -U telecom_user -d telecom_catalog -f add_business_to_server1.sql

\c telecom_catalog;

BEGIN;

SELECT '========================================' as status;
SELECT 'Adding Business Product to Server 1' as status;
SELECT '========================================' as status;

-- ================================================================
-- STEP 1: Create Business Service Specification
-- ================================================================

SELECT 'STEP 1: Creating Business Service Specification' as status;

-- Check if it already exists
SELECT CASE 
  WHEN EXISTS (SELECT 1 FROM service_specifications WHERE id = 'enterprise_fiber_1000')
  THEN '⚠️  Service specification already exists - skipping'
  ELSE '✓ Creating enterprise_fiber_1000 specification'
END as status;

-- Create enterprise fiber service specification
INSERT INTO service_specifications 
  (id, name, service_type, description)
VALUES 
  (
    'enterprise_fiber_1000',
    'Enterprise Fiber 1 Gbps',
    'business_fiber_internet',
    '1 Gbps dedicated fiber internet service for small businesses with 99.99% uptime SLA, static IP, priority support, and symmetric upload/download speeds'
  )
ON CONFLICT (id) DO NOTHING;

-- Verify creation
SELECT 
  '✓ Service Specification Created:' as status,
  id,
  name,
  service_type,
  description
FROM service_specifications
WHERE id = 'enterprise_fiber_1000';

-- ================================================================
-- STEP 2: Create Business Product Offering
-- ================================================================

SELECT 'STEP 2: Creating Business Product Offering' as status;

-- Check if it already exists
SELECT CASE 
  WHEN EXISTS (SELECT 1 FROM product_offerings WHERE id = 'pkg_enterprise_fiber_1000')
  THEN '⚠️  Product offering already exists - skipping'
  ELSE '✓ Creating pkg_enterprise_fiber_1000 product'
END as status;

-- Create business product offering
INSERT INTO product_offerings 
  (id, name, description, category, price_monthly, price_setup, contract_length_months, is_active)
VALUES 
  (
    'pkg_enterprise_fiber_1000',
    'TeleCo Business Fiber Pro',
    'Dedicated 1 Gbps fiber internet designed for small businesses with guaranteed symmetric speeds, 99.99% uptime SLA, 5 static IP addresses, priority 24/7 support, and advanced security features',
    'business',
    179.99,
    299.99,
    24,
    true
  )
ON CONFLICT (id) DO NOTHING;

-- Verify creation
SELECT 
  '✓ Product Offering Created:' as status,
  id,
  name,
  category,
  price_monthly,
  price_setup,
  contract_length_months,
  is_active
FROM product_offerings
WHERE id = 'pkg_enterprise_fiber_1000';

-- ================================================================
-- STEP 3: Link Product to Service
-- ================================================================

SELECT 'STEP 3: Linking Product to Service Specification' as status;

-- Create the product-service link
INSERT INTO product_service_links 
  (product_offering_id, service_specification_id, is_primary)
VALUES 
  ('pkg_enterprise_fiber_1000', 'enterprise_fiber_1000', true)
ON CONFLICT DO NOTHING;

-- Verify link
SELECT 
  '✓ Product-Service Link Created:' as status,
  po.name as product_name,
  ss.name as service_name,
  psl.is_primary,
  psl.created_at
FROM product_service_links psl
JOIN product_offerings po ON psl.product_offering_id = po.id
JOIN service_specifications ss ON psl.service_specification_id = ss.id
WHERE po.id = 'pkg_enterprise_fiber_1000';

-- ================================================================
-- STEP 4: Add Business Fiber Coverage
-- ================================================================

SELECT 'STEP 4: Adding Business Fiber Coverage' as status;

-- Add business fiber to all locations with 1G+ consumer fiber
INSERT INTO service_coverage_new 
  (location_id, service_type, max_speed_mbps, coverage_quality, technology)
SELECT DISTINCT
  sc.location_id,
  'business_fiber_internet' as service_type,
  1000 as max_speed_mbps,
  'excellent' as coverage_quality,
  'fiber' as technology
FROM service_coverage_new sc
WHERE sc.service_type = 'fiber_internet' 
  AND sc.max_speed_mbps >= 1000
  AND NOT EXISTS (
    SELECT 1 
    FROM service_coverage_new sc2
    WHERE sc2.location_id = sc.location_id
      AND sc2.service_type = 'business_fiber_internet'
  );

-- Show business fiber coverage
SELECT 
  '✓ Business Fiber Coverage:' as status,
  COUNT(*) as locations_covered
FROM service_coverage_new
WHERE service_type = 'business_fiber_internet';

SELECT 
  gl.location_id,
  gl.street_number || ' ' || gl.street_name as address,
  gl.city,
  sc.max_speed_mbps,
  sc.coverage_quality
FROM geographic_locations gl
JOIN service_coverage_new sc ON gl.location_id = sc.location_id
WHERE sc.service_type = 'business_fiber_internet'
ORDER BY gl.city, gl.street_name;

-- ================================================================
-- STEP 5: Validation Summary
-- ================================================================

SELECT '========================================' as status;
SELECT 'Validation Summary' as status;
SELECT '========================================' as status;

-- Updated counts
SELECT 
  '✓ Updated Catalog Counts:' as metric,
  (SELECT COUNT(*) FROM service_specifications) as total_specs,
  (SELECT COUNT(*) FROM product_offerings WHERE is_active = true) as total_products,
  (SELECT COUNT(*) FROM product_service_links) as total_links;

-- Business product status
SELECT 
  '✓ Business Product Status:' as check,
  po.name,
  po.category,
  po.price_monthly,
  po.is_active,
  ss.name as linked_service,
  CASE 
    WHEN EXISTS (
      SELECT 1 FROM service_coverage_new 
      WHERE service_type = 'business_fiber_internet'
    ) THEN '✓ Has coverage'
    ELSE '✗ No coverage'
  END as coverage_status
FROM product_offerings po
JOIN product_service_links psl ON po.id = psl.product_offering_id
JOIN service_specifications ss ON psl.service_specification_id = ss.id
WHERE po.id = 'pkg_enterprise_fiber_1000';

SELECT '========================================' as status;
SELECT '✓ MIGRATION COMPLETE!' as status;
SELECT 'Server 1 now has business product!' as status;
SELECT '========================================' as status;

COMMIT;

-- ================================================================
-- Post-Migration Tests
-- ================================================================

\echo ''
\echo 'Test 1: Verify Business Product Exists'
SELECT 
  id,
  name,
  category,
  price_monthly
FROM product_offerings
WHERE id = 'pkg_enterprise_fiber_1000';

\echo ''
\echo 'Test 2: Verify Business Service Exists'
SELECT 
  id,
  name,
  service_type
FROM service_specifications
WHERE id = 'enterprise_fiber_1000';

\echo ''
\echo 'Test 3: Verify Product-Service Link'
SELECT 
  po.name as product,
  ss.name as service,
  psl.is_primary
FROM product_service_links psl
JOIN product_offerings po ON psl.product_offering_id = po.id
JOIN service_specifications ss ON psl.service_specification_id = ss.id
WHERE po.id = 'pkg_enterprise_fiber_1000';

\echo ''
\echo 'Test 4: Verify Coverage Exists'
SELECT COUNT(*) as business_fiber_locations
FROM service_coverage_new
WHERE service_type = 'business_fiber_internet';

\echo ''
\echo '✓ All tests complete. Server 1 now matches Server 2!'
