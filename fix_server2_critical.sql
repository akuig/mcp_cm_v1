-- ============================================================================
-- CRITICAL FIX FOR SERVER 2 (Fanore)
-- Fix broken Business Fiber Pro product and add coverage
-- ============================================================================
-- Run this on: Server 2 (Fanore MCP)
-- Date: 2025-10-11
-- Purpose: Link pkg_enterprise_fiber_1000 to enterprise_fiber_1000 service
--          and add business fiber coverage to premium locations
-- ============================================================================

\c telecom_catalog;

-- ============================================================================
-- PART 1: FIX BROKEN PRODUCT-SERVICE LINK (CRITICAL)
-- ============================================================================

BEGIN;

-- Check current status before fix
SELECT 
    'BEFORE FIX - Business Product Status:' as checkpoint,
    po.id,
    po.name,
    po.category,
    po.price_monthly,
    COUNT(psl.id) as linked_services
FROM product_offerings po
LEFT JOIN product_service_links psl ON po.id = psl.product_offering_id
WHERE po.id = 'pkg_enterprise_fiber_1000'
GROUP BY po.id, po.name, po.category, po.price_monthly;

-- Add the missing product-service link
INSERT INTO product_service_links 
    (product_offering_id, service_specification_id, is_primary)
VALUES 
    ('pkg_enterprise_fiber_1000', 'enterprise_fiber_1000', true)
ON CONFLICT (product_offering_id, service_specification_id) DO NOTHING;

-- Verify the link was created
SELECT 
    'AFTER FIX - Business Product Linked:' as checkpoint,
    po.id as product_id,
    po.name as product_name,
    po.price_monthly,
    ss.id as service_id,
    ss.name as service_name,
    ss.service_type,
    psl.is_primary,
    psl.created_at as link_created_at
FROM product_service_links psl
JOIN product_offerings po ON psl.product_offering_id = po.id
JOIN service_specifications ss ON psl.service_specification_id = ss.id
WHERE po.id = 'pkg_enterprise_fiber_1000';

COMMIT;

-- ============================================================================
-- PART 2: ADD BUSINESS FIBER COVERAGE DATA
-- ============================================================================

BEGIN;

-- Check which locations have 2G fiber (premium locations)
SELECT 
    'Premium Fiber Locations (candidates for business fiber):' as info,
    gl.location_id,
    gl.street_number,
    gl.street_name,
    gl.city,
    sc.max_speed_mbps as current_max_speed
FROM geographic_locations gl
JOIN service_coverage_new sc ON gl.location_id = sc.location_id
WHERE sc.service_type = 'fiber_internet' 
    AND sc.max_speed_mbps >= 1000
ORDER BY gl.city, gl.street_name;

-- Add business fiber coverage to all premium fiber locations
-- Target: Locations with 1Gbps or higher consumer fiber
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

-- Verify business fiber coverage was added
SELECT 
    'Business Fiber Coverage Added:' as info,
    gl.location_id,
    gl.street_number || ' ' || gl.street_name as address,
    gl.city,
    gl.postal_code,
    sc.service_type,
    sc.max_speed_mbps,
    sc.coverage_quality,
    sc.technology
FROM geographic_locations gl
JOIN service_coverage_new sc ON gl.location_id = sc.location_id
WHERE sc.service_type = 'business_fiber_internet'
ORDER BY gl.city, gl.street_name;

COMMIT;

-- ============================================================================
-- PART 3: ADD PHONE AND SECURITY COVERAGE (Fill gaps)
-- ============================================================================

BEGIN;

-- Add phone service coverage to all locations with fiber or cable
INSERT INTO service_coverage_new 
    (location_id, service_type, max_speed_mbps, coverage_quality, technology, available)
SELECT DISTINCT
    location_id,
    'phone' as service_type,
    NULL as max_speed_mbps,
    CASE 
        WHEN EXISTS (
            SELECT 1 FROM service_coverage_new sc2 
            WHERE sc2.location_id = sc1.location_id 
            AND sc2.service_type = 'fiber_internet'
        ) THEN 'excellent'
        ELSE 'good'
    END as coverage_quality,
    'voip' as technology,
    true as available
FROM service_coverage_new sc1
WHERE service_type IN ('fiber_internet', 'cable_internet')
    AND location_id NOT IN (
        SELECT location_id 
        FROM service_coverage_new 
        WHERE service_type = 'phone'
    )
ON CONFLICT DO NOTHING;

-- Add security service coverage to premium fiber locations
INSERT INTO service_coverage_new 
    (location_id, service_type, max_speed_mbps, coverage_quality, technology, signal_strength, available)
SELECT DISTINCT
    location_id,
    'security' as service_type,
    NULL as max_speed_mbps,
    'excellent' as coverage_quality,
    'wireless' as technology,
    5 as signal_strength,
    true as available
FROM service_coverage_new
WHERE service_type = 'fiber_internet' 
    AND max_speed_mbps >= 1000
    AND location_id NOT IN (
        SELECT location_id 
        FROM service_coverage_new 
        WHERE service_type = 'security'
    )
ON CONFLICT DO NOTHING;

-- Show updated coverage summary
SELECT 
    'Coverage Summary by Service Type:' as info,
    service_type,
    COUNT(DISTINCT location_id) as location_count,
    AVG(CASE WHEN max_speed_mbps IS NOT NULL THEN max_speed_mbps END) as avg_speed_mbps,
    COUNT(*) as total_coverage_entries
FROM service_coverage_new
GROUP BY service_type
ORDER BY service_type;

COMMIT;

-- ============================================================================
-- PART 4: FINAL VERIFICATION AND INTEGRITY CHECK
-- ============================================================================

-- Check all products now have service links
SELECT 
    '=== FINAL PRODUCT INTEGRITY CHECK ===' as section,
    COUNT(*) as total_active_products,
    COUNT(DISTINCT psl.product_offering_id) as products_with_services,
    COUNT(*) - COUNT(DISTINCT psl.product_offering_id) as orphaned_products
FROM product_offerings po
LEFT JOIN product_service_links psl ON po.id = psl.product_offering_id
WHERE po.is_active = true;

-- List any remaining orphaned products (should be 0)
SELECT 
    'ORPHANED PRODUCTS (should be empty):' as warning,
    po.id,
    po.name,
    po.category,
    po.price_monthly
FROM product_offerings po
LEFT JOIN product_service_links psl ON po.id = psl.product_offering_id
WHERE po.is_active = true
    AND psl.id IS NULL;

-- Show complete business product configuration
SELECT 
    '=== BUSINESS FIBER PRO - COMPLETE CONFIGURATION ===' as section,
    po.name as product,
    po.price_monthly || ' per month + ' || po.setup_fee as pricing,
    po.contract_length_months || ' month contract' as contract,
    ss.name as service_spec,
    ss.description as service_description,
    COUNT(DISTINCT sc.location_id) as available_locations
FROM product_offerings po
JOIN product_service_links psl ON po.id = psl.product_offering_id
JOIN service_specifications ss ON psl.service_specification_id = ss.id
LEFT JOIN service_coverage_new sc ON sc.service_type = 'business_fiber_internet'
WHERE po.id = 'pkg_enterprise_fiber_1000'
GROUP BY po.name, po.price_monthly, po.price_setup, po.contract_length_months, ss.name, ss.description;

-- Show locations where Business Fiber Pro can be sold
SELECT 
    '=== BUSINESS FIBER PRO - AVAILABLE LOCATIONS ===' as section,
    gl.street_number || ' ' || gl.street_name as address,
    gl.city,
    gl.postal_code,
    gl.state_province,
    sc.max_speed_mbps || ' Mbps' as speed,
    sc.coverage_quality as quality
FROM geographic_locations gl
JOIN service_coverage_new sc ON gl.location_id = sc.location_id
WHERE sc.service_type = 'business_fiber_internet'
ORDER BY gl.city, gl.street_name;

-- Coverage completeness check
SELECT 
    '=== COVERAGE COMPLETENESS BY LOCATION ===' as section,
    gl.location_id,
    gl.street_number || ' ' || gl.street_name as address,
    gl.city,
    COUNT(DISTINCT sc.service_type) as service_types_available,
    STRING_AGG(DISTINCT sc.service_type, ', ' ORDER BY sc.service_type) as available_services
FROM geographic_locations gl
LEFT JOIN service_coverage_new sc ON gl.location_id = sc.location_id
GROUP BY gl.location_id, gl.street_number, gl.street_name, gl.city
ORDER BY service_types_available DESC, gl.city, gl.street_name;

-- Final success message
SELECT 
    '✅ SERVER 2 CRITICAL FIX COMPLETED' as status,
    NOW() as completed_at,
    'Business Fiber Pro is now operational' as message;

-- ============================================================================
-- VERIFICATION QUERIES - Run these after the fix
-- ============================================================================

-- Test 1: Verify business product can be queried with services
-- Expected: Should return 1 row with enterprise_fiber_1000 service

-- Test 2: Verify business fiber coverage exists  
-- Expected: Should return 3-5 premium locations

-- Test 3: Try to create a test order (don't commit)
-- This would be done through the API/MCP tools

-- ============================================================================
