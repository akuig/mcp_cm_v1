-- ============================================================================
-- UPGRADE SERVER 1 (MCP Local) TO MATCH SERVER 2
-- Add Business/Enterprise capabilities from Server 2
-- ============================================================================
-- Run this on: Server 1 (MCP Local)
-- Date: 2025-10-11
-- Purpose: Add business fiber product and service specification to Server 1
--          to match Server 2's capabilities
-- ============================================================================

\c telecom_catalog;

BEGIN;

-- ============================================================================
-- PART 1: ADD ENTERPRISE FIBER SERVICE SPECIFICATION
-- ============================================================================

-- Check if already exists
SELECT 
    CASE 
        WHEN EXISTS (SELECT 1 FROM service_specifications WHERE id = 'enterprise_fiber_1000')
        THEN '⚠️  Enterprise spec already exists - skipping'
        ELSE '✓ Will create enterprise spec'
    END as status;

-- Create enterprise fiber service specification
INSERT INTO service_specifications 
    (id, name, service_type, description, created_at, updated_at)
VALUES (
    'enterprise_fiber_1000',
    'Enterprise Fiber 1 Gbps',
    'business_fiber_internet',
    '1 Gbps dedicated fiber internet service for small businesses with 99.99% uptime SLA, static IP, priority support, and symmetric upload/download speeds',
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
)
ON CONFLICT (id) DO UPDATE SET
    description = EXCLUDED.description,
    updated_at = CURRENT_TIMESTAMP;

-- Verify spec was created
SELECT 
    '✓ Enterprise Service Spec Created:' as status,
    id,
    name,
    service_type,
    description
FROM service_specifications
WHERE id = 'enterprise_fiber_1000';

-- ============================================================================
-- PART 2: ADD BUSINESS FIBER PRO PRODUCT OFFERING
-- ============================================================================

-- Check if already exists
SELECT 
    CASE 
        WHEN EXISTS (SELECT 1 FROM product_offerings WHERE id = 'pkg_enterprise_fiber_1000')
        THEN '⚠️  Business product already exists - skipping'
        ELSE '✓ Will create business product'
    END as status;

-- Create business fiber pro product
INSERT INTO product_offerings 
    (id, name, description, category, price_monthly, price_setup, contract_length_months, is_active, created_at, updated_at)
VALUES (
    'pkg_enterprise_fiber_1000',
    'TeleCo Business Fiber Pro',
    'Dedicated 1 Gbps fiber internet designed for small businesses with guaranteed symmetric speeds, 99.99% uptime SLA, 5 static IP addresses, priority 24/7 support, and advanced security features',
    'business',
    179.99,
    299.99,
    24,
    true,
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
)
ON CONFLICT (id) DO UPDATE SET
    description = EXCLUDED.description,
    price_monthly = EXCLUDED.price_monthly,
    price_setup = EXCLUDED.price_setup,
    updated_at = CURRENT_TIMESTAMP;

-- Verify product was created
SELECT 
    '✓ Business Product Created:' as status,
    id,
    name,
    category,
    price_monthly,
    price_setup,
    contract_length_months
FROM product_offerings
WHERE id = 'pkg_enterprise_fiber_1000';

-- ============================================================================
-- PART 3: LINK PRODUCT TO SERVICE (CRITICAL)
-- ============================================================================

-- Create the product-service link
INSERT INTO product_service_links 
    (product_offering_id, service_specification_id, is_primary)
VALUES 
    ('pkg_enterprise_fiber_1000', 'enterprise_fiber_1000', true)
ON CONFLICT (product_offering_id, service_specification_id) DO NOTHING;

-- Verify link was created
SELECT 
    '✓ Product-Service Link Created:' as status,
    po.name as product,
    ss.name as service,
    psl.is_primary,
    psl.created_at
FROM product_service_links psl
JOIN product_offerings po ON psl.product_offering_id = po.id
JOIN service_specifications ss ON psl.service_specification_id = ss.id
WHERE po.id = 'pkg_enterprise_fiber_1000';

-- ============================================================================
-- PART 4: ADD BUSINESS FIBER COVERAGE TO PREMIUM LOCATIONS
-- ============================================================================

-- Add business fiber coverage to locations with 1G+ consumer fiber
INSERT INTO service_coverage_new 
    (location_id, service_type, max_speed_mbps, coverage_quality, technology, available)
SELECT 
    DISTINCT location_id,
    'business_fiber_internet' as service_type,
    1000 as max_speed_mbps,
    'excellent' as coverage_quality,
    'fiber' as technology,
    true as available
FROM service_coverage_new
WHERE service_type = 'fiber_internet' 
    AND max_speed_mbps >= 1000
    AND location_id NOT IN (
        SELECT location_id 
        FROM service_coverage_new 
        WHERE service_type = 'business_fiber_internet'
    )
ON CONFLICT DO NOTHING;

-- Show business fiber coverage
SELECT 
    '✓ Business Fiber Coverage:' as status,
    gl.location_id,
    gl.street_number || ' ' || gl.street_name as address,
    gl.city,
    sc.max_speed_mbps,
    sc.coverage_quality
FROM geographic_locations gl
JOIN service_coverage_new sc ON gl.location_id = sc.location_id
WHERE sc.service_type = 'business_fiber_internet'
ORDER BY gl.city, gl.street_name;

-- ============================================================================
-- PART 5: UPDATE CATALOG SUMMARY
-- ============================================================================

-- Show updated product count by category
SELECT 
    '=== UPDATED PRODUCT CATALOG ===' as section,
    category,
    COUNT(*) as product_count,
    STRING_AGG(name, ', ') as products
FROM product_offerings
WHERE is_active = true
GROUP BY category
ORDER BY 
    CASE category
        WHEN 'internet' THEN 1
        WHEN 'tv' THEN 2
        WHEN 'mobile' THEN 3
        WHEN 'bundle' THEN 4
        WHEN 'business' THEN 5
        ELSE 6
    END;

-- Show all products with service counts
SELECT 
    '=== PRODUCT-SERVICE MAPPING ===' as section,
    po.category,
    po.name as product,
    po.price_monthly,
    COUNT(psl.id) as linked_services,
    STRING_AGG(ss.name, ', ') as services
FROM product_offerings po
LEFT JOIN product_service_links psl ON po.id = psl.product_offering_id
LEFT JOIN service_specifications ss ON psl.service_specification_id = ss.id
WHERE po.is_active = true
GROUP BY po.id, po.category, po.name, po.price_monthly
ORDER BY po.category, po.name;

COMMIT;

-- ============================================================================
-- VERIFICATION
-- ============================================================================

-- Final integrity check
SELECT 
    '✅ SERVER 1 UPGRADE COMPLETED' as status,
    COUNT(DISTINCT po.id) as total_products,
    COUNT(DISTINCT CASE WHEN po.category = 'business' THEN po.id END) as business_products,
    COUNT(DISTINCT psl.product_offering_id) as products_with_services,
    COUNT(DISTINCT po.id) - COUNT(DISTINCT psl.product_offering_id) as orphaned_products
FROM product_offerings po
LEFT JOIN product_service_links psl ON po.id = psl.product_offering_id
WHERE po.is_active = true;

-- Expected results:
-- total_products: 15
-- business_products: 1
-- products_with_services: 15
-- orphaned_products: 0

SELECT 
    '=== SERVER 1 NOW HAS ===' as summary,
    (SELECT COUNT(*) FROM service_specifications) as total_specs,
    (SELECT COUNT(*) FROM product_offerings WHERE is_active = true) as total_products,
    (SELECT COUNT(*) FROM product_service_links) as total_links,
    (SELECT COUNT(DISTINCT location_id) FROM service_coverage_new WHERE service_type = 'business_fiber_internet') as business_coverage_locations;

-- ============================================================================
