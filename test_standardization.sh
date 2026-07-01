#!/bin/bash
# ============================================================================
# Test and verify catalog standardization
# ============================================================================

echo "============================================================================"
echo "CATALOG STANDARDIZATION - VERIFICATION TESTS"
echo "============================================================================"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check Docker
if ! docker ps | grep -q telecom_postgres; then
    echo -e "${RED}❌ PostgreSQL container not running${NC}"
    exit 1
fi

echo -e "${GREEN}✓ PostgreSQL container running${NC}"
echo ""

# ============================================================================
# TEST 1: Catalog Entity Counts
# ============================================================================

echo "TEST 1: Checking catalog entity counts..."
RESULT=$(docker exec telecom_postgres psql -U telecom_user -d telecom_catalog -t -c "
SELECT 
  (SELECT COUNT(*) FROM service_specifications) as specs,
  (SELECT COUNT(*) FROM product_offerings WHERE is_active = true) as products,
  (SELECT COUNT(*) FROM product_service_links) as links;
")

SPECS=$(echo $RESULT | awk '{print $1}')
PRODUCTS=$(echo $RESULT | awk '{print $2}')
LINKS=$(echo $RESULT | awk '{print $3}')

echo "  Service Specifications: $SPECS (expected: 23)"
echo "  Product Offerings: $PRODUCTS (expected: 15)"
echo "  Product-Service Links: $LINKS (expected: 24)"

if [ "$SPECS" = "23" ] && [ "$PRODUCTS" = "15" ] && [ "$LINKS" = "24" ]; then
    echo -e "${GREEN}  ✓ PASS: Entity counts correct${NC}"
else
    echo -e "${RED}  ✗ FAIL: Entity counts incorrect${NC}"
fi
echo ""

# ============================================================================
# TEST 2: No Orphaned Products
# ============================================================================

echo "TEST 2: Checking for orphaned products..."
ORPHANED=$(docker exec telecom_postgres psql -U telecom_user -d telecom_catalog -t -c "
SELECT COUNT(*)
FROM product_offerings po
LEFT JOIN product_service_links psl ON po.id = psl.product_offering_id
WHERE po.is_active = true AND psl.id IS NULL;
")

ORPHANED=$(echo $ORPHANED | xargs)  # trim whitespace

if [ "$ORPHANED" = "0" ]; then
    echo -e "${GREEN}  ✓ PASS: No orphaned products${NC}"
else
    echo -e "${RED}  ✗ FAIL: Found $ORPHANED orphaned products${NC}"
    docker exec telecom_postgres psql -U telecom_user -d telecom_catalog -c "
    SELECT id, name, category FROM product_offerings po
    LEFT JOIN product_service_links psl ON po.id = psl.product_offering_id
    WHERE po.is_active = true AND psl.id IS NULL;
    "
fi
echo ""

# ============================================================================
# TEST 3: Business Fiber Pro Product Linked
# ============================================================================

echo "TEST 3: Checking Business Fiber Pro product..."
BUSINESS_LINKED=$(docker exec telecom_postgres psql -U telecom_user -d telecom_catalog -t -c "
SELECT COUNT(*)
FROM product_service_links
WHERE product_offering_id = 'pkg_enterprise_fiber_1000'
  AND service_specification_id = 'enterprise_fiber_1000';
")

BUSINESS_LINKED=$(echo $BUSINESS_LINKED | xargs)

if [ "$BUSINESS_LINKED" = "1" ]; then
    echo -e "${GREEN}  ✓ PASS: Business Fiber Pro properly linked${NC}"
else
    echo -e "${RED}  ✗ FAIL: Business Fiber Pro not linked${NC}"
fi
echo ""

# ============================================================================
# TEST 4: Business Fiber Coverage Exists
# ============================================================================

echo "TEST 4: Checking business fiber coverage..."
BUSINESS_COVERAGE=$(docker exec telecom_postgres psql -U telecom_user -d telecom_catalog -t -c "
SELECT COUNT(DISTINCT location_id)
FROM service_coverage_new
WHERE service_type = 'business_fiber_internet';
")

BUSINESS_COVERAGE=$(echo $BUSINESS_COVERAGE | xargs)

if [ "$BUSINESS_COVERAGE" -ge "3" ]; then
    echo -e "${GREEN}  ✓ PASS: Business fiber coverage exists at $BUSINESS_COVERAGE locations${NC}"
else
    echo -e "${RED}  ✗ FAIL: Insufficient business fiber coverage ($BUSINESS_COVERAGE locations)${NC}"
fi
echo ""

# ============================================================================
# TEST 5: All Bundles Have Multiple Services
# ============================================================================

echo "TEST 5: Checking bundle configurations..."
BUNDLES_OK=$(docker exec telecom_postgres psql -U telecom_user -d telecom_catalog -t -c "
SELECT COUNT(*)
FROM (
  SELECT product_offering_id, COUNT(*) as service_count
  FROM product_service_links psl
  JOIN product_offerings po ON psl.product_offering_id = po.id
  WHERE po.category = 'bundle'
  GROUP BY product_offering_id
  HAVING COUNT(*) >= 2
) as bundle_check;
")

BUNDLES_OK=$(echo $BUNDLES_OK | xargs)

if [ "$BUNDLES_OK" = "4" ]; then
    echo -e "${GREEN}  ✓ PASS: All 4 bundles have multiple services${NC}"
else
    echo -e "${RED}  ✗ FAIL: Some bundles missing services${NC}"
fi
echo ""

# ============================================================================
# TEST 6: Service Specification Utilization
# ============================================================================

echo "TEST 6: Checking service specification utilization..."
UTIL=$(docker exec telecom_postgres psql -U telecom_user -d telecom_catalog -t -c "
SELECT 
  COUNT(DISTINCT ss.id) as total,
  COUNT(DISTINCT psl.service_specification_id) as used,
  ROUND(100.0 * COUNT(DISTINCT psl.service_specification_id) / COUNT(DISTINCT ss.id)) as pct
FROM service_specifications ss
LEFT JOIN product_service_links psl ON ss.id = psl.service_specification_id;
")

TOTAL_SPECS=$(echo $UTIL | awk '{print $1}')
USED_SPECS=$(echo $UTIL | awk '{print $2}')
UTIL_PCT=$(echo $UTIL | awk '{print $3}')

echo "  Total specs: $TOTAL_SPECS"
echo "  Specs in use: $USED_SPECS"
echo "  Utilization: $UTIL_PCT%"

if [ "$USED_SPECS" -ge "12" ]; then
    echo -e "${GREEN}  ✓ PASS: Acceptable utilization${NC}"
else
    echo -e "${YELLOW}  ⚠ WARNING: Low utilization${NC}"
fi
echo ""

# ============================================================================
# TEST 7: Geographic Coverage
# ============================================================================

echo "TEST 7: Checking geographic coverage..."
LOCATIONS=$(docker exec telecom_postgres psql -U telecom_user -d telecom_catalog -t -c "
SELECT COUNT(*) FROM geographic_locations;
")

LOCATIONS=$(echo $LOCATIONS | xargs)

if [ "$LOCATIONS" = "7" ]; then
    echo -e "${GREEN}  ✓ PASS: All 7 locations present${NC}"
else
    echo -e "${YELLOW}  ⚠ WARNING: Expected 7 locations, found $LOCATIONS${NC}"
fi
echo ""

# ============================================================================
# SUMMARY
# ============================================================================

echo "============================================================================"
echo "VERIFICATION SUMMARY"
echo "============================================================================"
echo ""

# Count passes
docker exec telecom_postgres psql -U telecom_user -d telecom_catalog -c "
SELECT 
  '=== CATALOG HEALTH SUMMARY ===' as section,
  (SELECT COUNT(*) FROM service_specifications) || ' service specs' as specs,
  (SELECT COUNT(*) FROM product_offerings WHERE is_active = true) || ' products' as products,
  (SELECT COUNT(*) FROM product_service_links) || ' links' as links,
  (SELECT COUNT(*) FROM geographic_locations) || ' locations' as locations,
  CASE 
    WHEN EXISTS (
      SELECT 1 FROM product_offerings po
      LEFT JOIN product_service_links psl ON po.id = psl.product_offering_id
      WHERE po.is_active = true AND psl.id IS NULL
    ) THEN '❌ HAS ORPHANED PRODUCTS'
    ELSE '✅ NO ORPHANED PRODUCTS'
  END as integrity;
"

echo ""
echo "Detailed product-service mapping:"
docker exec telecom_postgres psql -U telecom_user -d telecom_catalog -c "
SELECT 
  po.category,
  po.name as product,
  COUNT(psl.id) as services_linked
FROM product_offerings po
LEFT JOIN product_service_links psl ON po.id = psl.product_offering_id
WHERE po.is_active = true
GROUP BY po.category, po.name
ORDER BY po.category, po.name;
"

echo ""
echo -e "${GREEN}============================================================================${NC}"
echo -e "${GREEN}✅ VERIFICATION COMPLETE${NC}"
echo -e "${GREEN}============================================================================${NC}"
echo ""
echo "If all tests passed, your catalog is properly standardized!"
echo "If any tests failed, review the output above and re-run the appropriate scripts."
echo ""
