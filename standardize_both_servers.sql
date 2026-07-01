-- ============================================================================
-- STANDARDIZE BOTH SERVERS - COMPLETE CATALOG SYNC
-- Make Server 1 and Server 2 identical
-- ============================================================================
-- Run this on: BOTH Server 1 (MCP Local) AND Server 2 (Fanore)
-- Date: 2025-10-11
-- Purpose: Ensure both servers have identical catalog data
-- Prerequisites: 
--   1. Run fix_server2_critical.sql on Server 2 first
--   2. Run upgrade_server1_to_match_server2.sql on Server 1 first
-- ============================================================================

\c telecom_catalog;

BEGIN;

-- ============================================================================
-- STEP 1: VERIFY STARTING STATE
-- ============================================================================

SELECT '=== STARTING STATE VERIFICATION ===' as step;

-- Count current entities
SELECT 
    'Current Catalog Size:' as metric,
    (SELECT COUNT(*) FROM service_specifications) as specs,
    (SELECT COUNT(*) FROM product_offerings WHERE is_active = true) as products,
    (SELECT COUNT(*) FROM product_service_links) as links,
    (SELECT COUNT(*) FROM geographic_locations) as locations,
    (SELECT COUNT(DISTINCT location_id) FROM service_coverage_new) as locations_with_coverage;

-- Check for orphaned products
SELECT 
    'Orphaned Products Check:' as check,
    COUNT(*) as orphaned_count
FROM product_offerings po
LEFT JOIN product_service_links psl ON po.id = psl.product_offering_id
WHERE po.is_active = true AND psl.id IS NULL;

-- ============================================================================
-- STEP 2: STANDARDIZE SERVICE SPECIFICATIONS (23 specs)
-- ============================================================================

SELECT '=== STANDARDIZING SERVICE SPECIFICATIONS ===' as step;

-- Ensure all 23 specs exist with correct descriptions
-- Internet specs
INSERT INTO service_specifications (id, name, service_type, description, created_at, updated_at) VALUES
    ('cable_100', 'Cable 100 Mbps', 'cable_internet', '100 Mbps cable internet service', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('cable_200', 'Cable 200 Mbps', 'cable_internet', '200 Mbps cable internet service', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('cable_400', 'Cable 400 Mbps', 'cable_internet', '400 Mbps cable internet service', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('dsl_25', 'DSL 25 Mbps', 'dsl_internet', '25 Mbps DSL internet service', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('dsl_50', 'DSL 50 Mbps', 'dsl_internet', '50 Mbps DSL internet service', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('fiber_500', 'Fiber 500 Mbps', 'fiber_internet', '500 Mbps fiber internet service with 99.9% uptime SLA', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('fiber_1000', 'Fiber 1 Gbps', 'fiber_internet', '1 Gbps fiber internet service with 99.9% uptime SLA', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('fiber_2000', 'Fiber 2 Gbps', 'fiber_internet', '2 Gbps fiber internet service for power users', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('wireless_50', 'Wireless 50 Mbps', 'wireless_broadband', '50 Mbps 5G wireless internet', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('wireless_150', 'Wireless 150 Mbps', 'wireless_broadband', '150 Mbps 5G wireless internet', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('wireless_300', 'Wireless 300 Mbps', 'wireless_broadband', '300 Mbps 5G+ wireless internet', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('enterprise_fiber_1000', 'Enterprise Fiber 1 Gbps', 'business_fiber_internet', '1 Gbps dedicated fiber internet service for small businesses with 99.99% uptime SLA, static IP, priority support, and symmetric upload/download speeds', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    updated_at = CURRENT_TIMESTAMP;

-- TV specs
INSERT INTO service_specifications (id, name, service_type, description, created_at, updated_at) VALUES
    ('tv_basic', 'Basic TV Package', 'tv', '50+ channels including local and news', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('tv_premium', 'Premium TV Package', 'tv', '200+ channels including sports and movies', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('tv_streaming', 'Streaming TV Service', 'tv', 'Cloud-based TV streaming with 100+ channels', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('tv_ultimate', 'Ultimate TV Package', 'tv', '400+ channels with all premium content', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    updated_at = CURRENT_TIMESTAMP;

-- Mobile specs
INSERT INTO service_specifications (id, name, service_type, description, created_at, updated_at) VALUES
    ('mobile_5gb', 'Mobile 5GB Plan', 'mobile', '5GB monthly data with unlimited calls/texts', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('mobile_25gb', 'Mobile 25GB Plan', 'mobile', '25GB monthly data with unlimited calls/texts', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('mobile_unlimited', 'Mobile Unlimited Plan', 'mobile', 'Unlimited 5G data, calls, and texts', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    updated_at = CURRENT_TIMESTAMP;

-- Phone specs
INSERT INTO service_specifications (id, name, service_type, description, created_at, updated_at) VALUES
    ('phone_basic', 'Basic Home Phone', 'phone', 'Unlimited local and long distance calling', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('phone_international', 'International Home Phone', 'phone', 'Unlimited calling including international', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    updated_at = CURRENT_TIMESTAMP;

-- Security specs
INSERT INTO service_specifications (id, name, service_type, description, created_at, updated_at) VALUES
    ('security_basic', 'Basic Home Security', 'security', 'Door/window sensors with mobile monitoring', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('security_premium', 'Premium Home Security', 'security', 'Full home security with cameras and professional monitoring', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    updated_at = CURRENT_TIMESTAMP;

SELECT 
    '✓ Service Specifications Standardized:' as status,
    COUNT(*) as total_specs
FROM service_specifications;

-- ============================================================================
-- STEP 3: STANDARDIZE PRODUCT OFFERINGS (15 products)
-- ============================================================================

SELECT '=== STANDARDIZING PRODUCT OFFERINGS ===' as step;

-- Internet products
INSERT INTO product_offerings (id, name, description, category, price_monthly, price_setup, contract_length_months, is_active) VALUES
    ('pkg_fiber_500', 'TeleCo Fiber 500', 'High-speed 500 Mbps fiber internet', 'internet', 59.99, 99.99, 12, true),
    ('pkg_fiber_1000', 'TeleCo Fiber Gig', 'Ultra-fast 1 Gbps fiber internet', 'internet', 79.99, 99.99, 12, true),
    ('pkg_fiber_2000', 'TeleCo Fiber Pro', 'Professional 2 Gbps fiber for power users', 'internet', 129.99, 199.99, 24, true),
    ('pkg_cable_400', 'TeleCo Cable Max', 'High-speed 400 Mbps cable internet', 'internet', 49.99, 49.99, 12, true),
    ('pkg_wireless_300', 'TeleCo 5G Home', 'Ultra-fast 5G+ wireless internet', 'internet', 69.99, 0.00, 0, true)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    price_monthly = EXCLUDED.price_monthly,
    price_setup = EXCLUDED.price_setup,
    contract_length_months = EXCLUDED.contract_length_months,
    updated_at = CURRENT_TIMESTAMP;

-- TV products
INSERT INTO product_offerings (id, name, description, category, price_monthly, price_setup, contract_length_months, is_active) VALUES
    ('pkg_tv_basic', 'TeleCo Basic TV', 'Essential TV package with local channels', 'tv', 29.99, 0.00, 12, true),
    ('pkg_tv_premium', 'TeleCo Premium TV', 'Premium TV with sports and movies', 'tv', 79.99, 49.99, 12, true),
    ('pkg_tv_streaming', 'TeleCo Stream TV', 'Next-gen streaming TV service', 'tv', 39.99, 0.00, 0, true)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    price_monthly = EXCLUDED.price_monthly,
    updated_at = CURRENT_TIMESTAMP;

-- Mobile products
INSERT INTO product_offerings (id, name, description, category, price_monthly, price_setup, contract_length_months, is_active) VALUES
    ('pkg_mobile_family', 'TeleCo Family Mobile', 'Family mobile plan with unlimited data', 'mobile', 120.00, 0.00, 24, true),
    ('pkg_mobile_unlimited', 'TeleCo Unlimited Mobile', 'Single line unlimited mobile', 'mobile', 65.00, 0.00, 0, true)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    price_monthly = EXCLUDED.price_monthly,
    updated_at = CURRENT_TIMESTAMP;

-- Bundle products
INSERT INTO product_offerings (id, name, description, category, price_monthly, price_setup, contract_length_months, is_active) VALUES
    ('pkg_triple_play', 'TeleCo Triple Play', 'Internet + TV + Phone bundle', 'bundle', 99.99, 99.99, 24, true),
    ('pkg_double_play_it', 'TeleCo Internet + TV', 'High-speed internet and premium TV', 'bundle', 89.99, 49.99, 12, true),
    ('pkg_smart_home', 'TeleCo Smart Home', 'Internet + TV + Security bundle', 'bundle', 119.99, 199.99, 24, true),
    ('pkg_everything', 'TeleCo Everything', 'Complete home connectivity solution', 'bundle', 149.99, 199.99, 24, true)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    price_monthly = EXCLUDED.price_monthly,
    updated_at = CURRENT_TIMESTAMP;

-- Business product
INSERT INTO product_offerings (id, name, description, category, price_monthly, price_setup, contract_length_months, is_active) VALUES
    ('pkg_enterprise_fiber_1000', 'TeleCo Business Fiber Pro', 'Dedicated 1 Gbps fiber internet designed for small businesses with guaranteed symmetric speeds, 99.99% uptime SLA, 5 static IP addresses, priority 24/7 support, and advanced security features', 'business', 179.99, 299.99, 24, true)
ON CONFLICT (id) DO UPDATE SET
    name = EXCLUDED.name,
    description = EXCLUDED.description,
    price_monthly = EXCLUDED.price_monthly,
    updated_at = CURRENT_TIMESTAMP;

SELECT 
    '✓ Product Offerings Standardized:' as status,
    COUNT(*) as total_products
FROM product_offerings
WHERE is_active = true;

-- ============================================================================
-- STEP 4: STANDARDIZE PRODUCT-SERVICE LINKS (24 links)
-- ============================================================================

SELECT '=== STANDARDIZING PRODUCT-SERVICE LINKS ===' as step;

-- Clear any existing links and rebuild from scratch for consistency
DELETE FROM product_service_links;

-- Internet product links
INSERT INTO product_service_links (product_offering_id, service_specification_id, is_primary) VALUES
    ('pkg_fiber_500', 'fiber_500', true),
    ('pkg_fiber_1000', 'fiber_1000', true),
    ('pkg_fiber_2000', 'fiber_2000', true),
    ('pkg_cable_400', 'cable_400', true),
    ('pkg_wireless_300', 'wireless_300', true);

-- TV product links
INSERT INTO product_service_links (product_offering_id, service_specification_id, is_primary) VALUES
    ('pkg_tv_basic', 'tv_basic', true),
    ('pkg_tv_premium', 'tv_premium', true),
    ('pkg_tv_streaming', 'tv_streaming', true);

-- Mobile product links
INSERT INTO product_service_links (product_offering_id, service_specification_id, is_primary) VALUES
    ('pkg_mobile_family', 'mobile_unlimited', true),
    ('pkg_mobile_unlimited', 'mobile_unlimited', true);

-- Bundle: Triple Play
INSERT INTO product_service_links (product_offering_id, service_specification_id, is_primary) VALUES
    ('pkg_triple_play', 'fiber_1000', true),
    ('pkg_triple_play', 'tv_premium', false),
    ('pkg_triple_play', 'phone_basic', false);

-- Bundle: Double Play (Internet + TV)
INSERT INTO product_service_links (product_offering_id, service_specification_id, is_primary) VALUES
    ('pkg_double_play_it', 'fiber_500', true),
    ('pkg_double_play_it', 'tv_premium', false);

-- Bundle: Smart Home
INSERT INTO product_service_links (product_offering_id, service_specification_id, is_primary) VALUES
    ('pkg_smart_home', 'fiber_1000', true),
    ('pkg_smart_home', 'tv_basic', false),
    ('pkg_smart_home', 'security_premium', false);

-- Bundle: Everything
INSERT INTO product_service_links (product_offering_id, service_specification_id, is_primary) VALUES
    ('pkg_everything', 'fiber_2000', true),
    ('pkg_everything', 'tv_ultimate', false),
    ('pkg_everything', 'phone_international', false),
    ('pkg_everything', 'mobile_unlimited', false),
    ('pkg_everything', 'security_premium', false);

-- Business product link (CRITICAL)
INSERT INTO product_service_links (product_offering_id, service_specification_id, is_primary) VALUES
    ('pkg_enterprise_fiber_1000', 'enterprise_fiber_1000', true);

SELECT 
    '✓ Product-Service Links Standardized:' as status,
    COUNT(*) as total_links
FROM product_service_links;

-- ============================================================================
-- STEP 5: VERIFY STANDARDIZATION
-- ============================================================================

SELECT '=== STANDARDIZATION VERIFICATION ===' as step;

-- Count everything
SELECT 
    'Final Catalog State:' as metric,
    (SELECT COUNT(*) FROM service_specifications) as specs,
    (SELECT COUNT(*) FROM product_offerings WHERE is_active = true) as products,
    (SELECT COUNT(*) FROM product_service_links) as links,
    (SELECT COUNT(*) FROM geographic_locations) as locations;

-- Verify no orphaned products
SELECT 
    'Orphaned Products (should be 0):' as check,
    COUNT(*) as count
FROM product_offerings po
LEFT JOIN product_service_links psl ON po.id = psl.product_offering_id
WHERE po.is_active = true AND psl.id IS NULL;

-- Show products by category
SELECT 
    'Products by Category:' as summary,
    category,
    COUNT(*) as count,
    STRING_AGG(name, ', ') as products
FROM product_offerings
WHERE is_active = true
GROUP BY category
ORDER BY category;

-- Show service utilization
SELECT 
    'Service Specification Utilization:' as summary,
    COUNT(DISTINCT ss.id) as total_specs,
    COUNT(DISTINCT psl.service_specification_id) as used_specs,
    COUNT(DISTINCT ss.id) - COUNT(DISTINCT psl.service_specification_id) as unused_specs,
    ROUND(100.0 * COUNT(DISTINCT psl.service_specification_id) / COUNT(DISTINCT ss.id), 1) as utilization_pct
FROM service_specifications ss
LEFT JOIN product_service_links psl ON ss.id = psl.service_specification_id;

COMMIT;

-- ============================================================================
-- FINAL STATUS
-- ============================================================================

SELECT 
    '✅ CATALOG STANDARDIZATION COMPLETE' as status,
    NOW() as completed_at,
    'Both servers now have identical catalog structure' as message;

SELECT 
    '=== STANDARDIZED CATALOG SUMMARY ===' as summary,
    (SELECT COUNT(*) FROM service_specifications) || ' service specifications' as specs,
    (SELECT COUNT(*) FROM product_offerings WHERE is_active = true) || ' active products' as products,
    (SELECT COUNT(*) FROM product_service_links) || ' product-service links' as links,
    (SELECT COUNT(*) FROM geographic_locations) || ' geographic locations' as locations;

-- Expected values:
-- 23 service specifications
-- 15 active products  
-- 24 product-service links
-- 7 geographic locations

-- ============================================================================
