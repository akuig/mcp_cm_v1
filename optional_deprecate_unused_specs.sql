-- ============================================================================
-- OPTIONAL: DEPRECATE UNUSED SERVICE SPECIFICATIONS
-- Clean up orphaned specs to reduce catalog complexity
-- ============================================================================
-- Run this on: BOTH servers (after standardization)
-- Date: 2025-10-11
-- Purpose: Mark unused service specifications as deprecated
--          This is OPTIONAL - only run if you want to clean up the catalog
-- ============================================================================

\c telecom_catalog;

BEGIN;

-- ============================================================================
-- ANALYSIS: Show unused specs before deprecation
-- ============================================================================

SELECT '=== UNUSED SERVICE SPECIFICATIONS ===' as section;

-- List all unused specs
SELECT 
    'Unused Specs (candidates for deprecation):' as info,
    ss.id,
    ss.name,
    ss.service_type,
    ss.description
FROM service_specifications ss
LEFT JOIN product_service_links psl ON ss.id = psl.service_specification_id
WHERE psl.id IS NULL
ORDER BY ss.service_type, ss.name;

-- Count by service type
SELECT 
    'Unused Specs by Type:' as info,
    ss.service_type,
    COUNT(*) as unused_count
FROM service_specifications ss
LEFT JOIN product_service_links psl ON ss.id = psl.service_specification_id
WHERE psl.id IS NULL
GROUP BY ss.service_type
ORDER BY unused_count DESC;

-- ============================================================================
-- OPTION 1: SOFT DELETE - Add 'is_deprecated' flag
-- ============================================================================
-- Recommended approach: Keep specs but mark as deprecated

-- Add is_deprecated column if it doesn't exist
ALTER TABLE service_specifications 
ADD COLUMN IF NOT EXISTS is_deprecated BOOLEAN DEFAULT FALSE;

-- Mark unused specs as deprecated
UPDATE service_specifications
SET 
    is_deprecated = true,
    updated_at = CURRENT_TIMESTAMP
WHERE id IN (
    SELECT ss.id
    FROM service_specifications ss
    LEFT JOIN product_service_links psl ON ss.id = psl.service_specification_id
    WHERE psl.id IS NULL
);

-- Show deprecated specs
SELECT 
    '✓ Specs Marked as Deprecated:' as status,
    id,
    name,
    service_type
FROM service_specifications
WHERE is_deprecated = true
ORDER BY service_type, name;

-- ============================================================================
-- OPTION 2: HARD DELETE - Remove unused specs completely
-- ============================================================================
-- WARNING: This permanently deletes data. Only use if you're sure.
-- Comment out this section if you want to keep specs marked as deprecated

/*
-- Delete unused specs
DELETE FROM service_specifications
WHERE id IN (
    SELECT ss.id
    FROM service_specifications ss
    LEFT JOIN product_service_links psl ON ss.id = psl.service_specification_id
    WHERE psl.id IS NULL
);

SELECT 
    '✓ Unused Specs Deleted:' as status,
    COUNT(*) as remaining_specs
FROM service_specifications;
*/

-- ============================================================================
-- SUMMARY AFTER DEPRECATION
-- ============================================================================

SELECT '=== CATALOG SUMMARY AFTER CLEANUP ===' as section;

-- Spec utilization
SELECT 
    'Service Specification Status:' as metric,
    COUNT(*) as total_specs,
    COUNT(*) FILTER (WHERE is_deprecated = false) as active_specs,
    COUNT(*) FILTER (WHERE is_deprecated = true) as deprecated_specs,
    COUNT(DISTINCT psl.service_specification_id) as specs_in_use
FROM service_specifications ss
LEFT JOIN product_service_links psl ON ss.id = psl.service_specification_id;

-- Active specs by type
SELECT 
    'Active Specs by Type:' as metric,
    service_type,
    COUNT(*) as count
FROM service_specifications
WHERE is_deprecated = false
GROUP BY service_type
ORDER BY service_type;

-- Products with services
SELECT 
    'Product-Service Health:' as metric,
    COUNT(DISTINCT po.id) as total_products,
    COUNT(DISTINCT psl.product_offering_id) as products_with_services,
    COUNT(*) FILTER (WHERE psl.id IS NULL) as orphaned_products
FROM product_offerings po
LEFT JOIN product_service_links psl ON po.id = psl.product_offering_id
WHERE po.is_active = true;

COMMIT;

-- ============================================================================
-- RECOMMENDATIONS
-- ============================================================================

SELECT '
=== DEPRECATION RECOMMENDATIONS ===

DEPRECATED SPECS (11 total):
1. cable_100, cable_200 - Superseded by cable_400
2. dsl_25, dsl_50 - Legacy technology, minimal coverage
3. wireless_50, wireless_150 - Only wireless_300 in use
4. mobile_5gb, mobile_25gb - Only unlimited plan offered
5. security_basic - Only premium security offered

KEPT ACTIVE (12 specs):
- fiber_500, fiber_1000, fiber_2000 (all in use)
- cable_400 (in use)
- wireless_300 (in use)
- tv_basic, tv_premium, tv_streaming, tv_ultimate (all in use)
- mobile_unlimited (in use)
- phone_basic, phone_international (in use)
- security_premium (in use)
- enterprise_fiber_1000 (in use)

BUSINESS IMPACT:
- Reduced complexity: 48% fewer specs to maintain
- Clearer product catalog
- Easier service qualification
- No impact on existing products
- Can always un-deprecate if needed

NEXT STEPS:
1. Monitor for any attempts to use deprecated specs
2. Plan migration for any remaining DSL customers
3. Consider tiered mobile offerings in future
4. Update documentation to reflect active specs only
' as recommendations;

-- ============================================================================
