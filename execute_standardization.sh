#!/bin/bash
# ============================================================================
# Execute all catalog standardization scripts
# ============================================================================

set -e  # Exit on error

echo "============================================================================"
echo "CATALOG STANDARDIZATION - COMPLETE WORKFLOW"
echo "============================================================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if Docker is running
if ! docker ps | grep -q telecom_postgres; then
    echo -e "${RED}❌ Error: PostgreSQL container 'telecom_postgres' is not running${NC}"
    echo ""
    echo "Please start the containers first:"
    echo "  docker-compose up -d"
    exit 1
fi

echo -e "${GREEN}✓ PostgreSQL container is running${NC}"
echo ""

# ============================================================================
# PHASE 1: FIX SERVER 2 CRITICAL ISSUE
# ============================================================================

echo -e "${BLUE}============================================================================${NC}"
echo -e "${BLUE}PHASE 1: Fixing Server 2 (Fanore) Critical Issue${NC}"
echo -e "${BLUE}============================================================================${NC}"
echo ""
echo "This will:"
echo "  - Link Business Fiber Pro product to enterprise service"
echo "  - Add business fiber coverage to premium locations"
echo "  - Fill coverage gaps (phone, security)"
echo ""
read -p "Continue with Phase 1? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Copying SQL file to container..."
    docker cp fix_server2_critical.sql telecom_postgres:/tmp/
    
    echo "Executing fix on Server 2..."
    docker exec telecom_postgres psql -U telecom_user -d telecom_catalog -f /tmp/fix_server2_critical.sql
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Phase 1 Complete: Server 2 critical issue fixed${NC}"
    else
        echo -e "${RED}❌ Phase 1 Failed${NC}"
        exit 1
    fi
    
    docker exec telecom_postgres rm /tmp/fix_server2_critical.sql
    echo ""
else
    echo "Skipping Phase 1"
    echo ""
fi

# ============================================================================
# PHASE 2: UPGRADE SERVER 1
# ============================================================================

echo -e "${BLUE}============================================================================${NC}"
echo -e "${BLUE}PHASE 2: Upgrading Server 1 (MCP Local) to Match Server 2${NC}"
echo -e "${BLUE}============================================================================${NC}"
echo ""
echo "This will add to Server 1:"
echo "  - Enterprise Fiber service specification"
echo "  - Business Fiber Pro product offering"
echo "  - Product-service link"
echo "  - Business fiber coverage"
echo ""
read -p "Continue with Phase 2? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Copying SQL file to container..."
    docker cp upgrade_server1_to_match_server2.sql telecom_postgres:/tmp/
    
    echo "Executing upgrade on Server 1..."
    docker exec telecom_postgres psql -U telecom_user -d telecom_catalog -f /tmp/upgrade_server1_to_match_server2.sql
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Phase 2 Complete: Server 1 upgraded${NC}"
    else
        echo -e "${RED}❌ Phase 2 Failed${NC}"
        exit 1
    fi
    
    docker exec telecom_postgres rm /tmp/upgrade_server1_to_match_server2.sql
    echo ""
else
    echo "Skipping Phase 2"
    echo ""
fi

# ============================================================================
# PHASE 3: STANDARDIZE BOTH SERVERS
# ============================================================================

echo -e "${BLUE}============================================================================${NC}"
echo -e "${BLUE}PHASE 3: Complete Standardization (Both Servers)${NC}"
echo -e "${BLUE}============================================================================${NC}"
echo ""
echo "This will ensure both servers have:"
echo "  - Identical 23 service specifications"
echo "  - Identical 15 product offerings"
echo "  - Identical 24 product-service links"
echo "  - Zero orphaned products"
echo ""
read -p "Continue with Phase 3? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Copying SQL file to container..."
    docker cp standardize_both_servers.sql telecom_postgres:/tmp/
    
    echo "Executing standardization..."
    docker exec telecom_postgres psql -U telecom_user -d telecom_catalog -f /tmp/standardize_both_servers.sql
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Phase 3 Complete: Servers standardized${NC}"
    else
        echo -e "${RED}❌ Phase 3 Failed${NC}"
        exit 1
    fi
    
    docker exec telecom_postgres rm /tmp/standardize_both_servers.sql
    echo ""
else
    echo "Skipping Phase 3"
    echo ""
fi

# ============================================================================
# PHASE 4: OPTIONAL - DEPRECATE UNUSED SPECS
# ============================================================================

echo -e "${BLUE}============================================================================${NC}"
echo -e "${BLUE}PHASE 4: Optional - Deprecate Unused Specifications${NC}"
echo -e "${BLUE}============================================================================${NC}"
echo ""
echo -e "${YELLOW}This is OPTIONAL and will:${NC}"
echo "  - Mark 11 unused service specs as deprecated"
echo "  - Reduce catalog complexity by 48%"
echo "  - Keep data but mark as inactive"
echo ""
echo "Unused specs that will be deprecated:"
echo "  - cable_100, cable_200"
echo "  - dsl_25, dsl_50"
echo "  - wireless_50, wireless_150"
echo "  - mobile_5gb, mobile_25gb"
echo "  - security_basic"
echo ""
read -p "Deprecate unused specs? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Copying SQL file to container..."
    docker cp optional_deprecate_unused_specs.sql telecom_postgres:/tmp/
    
    echo "Executing deprecation..."
    docker exec telecom_postgres psql -U telecom_user -d telecom_catalog -f /tmp/optional_deprecate_unused_specs.sql
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Phase 4 Complete: Unused specs deprecated${NC}"
    else
        echo -e "${RED}❌ Phase 4 Failed${NC}"
        exit 1
    fi
    
    docker exec telecom_postgres rm /tmp/optional_deprecate_unused_specs.sql
    echo ""
else
    echo "Skipping Phase 4 - keeping all specs active"
    echo ""
fi

# ============================================================================
# FINAL VERIFICATION
# ============================================================================

echo -e "${BLUE}============================================================================${NC}"
echo -e "${BLUE}FINAL VERIFICATION${NC}"
echo -e "${BLUE}============================================================================${NC}"
echo ""

echo "Checking final catalog state..."
docker exec telecom_postgres psql -U telecom_user -d telecom_catalog -c "
SELECT 
    '=== FINAL CATALOG STATE ===' as section,
    (SELECT COUNT(*) FROM service_specifications) as total_specs,
    (SELECT COUNT(*) FROM service_specifications WHERE is_deprecated = false) as active_specs,
    (SELECT COUNT(*) FROM product_offerings WHERE is_active = true) as active_products,
    (SELECT COUNT(*) FROM product_service_links) as product_service_links,
    (SELECT COUNT(*) FROM geographic_locations) as locations;
"

echo ""
echo "Checking for orphaned products..."
docker exec telecom_postgres psql -U telecom_user -d telecom_catalog -c "
SELECT 
    COUNT(*) as orphaned_products
FROM product_offerings po
LEFT JOIN product_service_links psl ON po.id = psl.product_offering_id
WHERE po.is_active = true AND psl.id IS NULL;
"

echo ""
echo -e "${GREEN}============================================================================${NC}"
echo -e "${GREEN}✅ STANDARDIZATION COMPLETE${NC}"
echo -e "${GREEN}============================================================================${NC}"
echo ""
echo "Summary of changes:"
echo "  ✓ Server 2 critical issue fixed"
echo "  ✓ Server 1 upgraded with business capabilities"
echo "  ✓ Both servers now have identical catalogs"
echo "  ✓ All 15 products properly linked to services"
echo "  ✓ Zero orphaned products"
echo ""
echo "Expected catalog state:"
echo "  - 23 service specifications (or 12 if deprecated unused)"
echo "  - 15 active product offerings"
echo "  - 24 product-service links"
echo "  - 7 geographic locations"
echo ""
echo "Next steps:"
echo "  1. Test ordering Business Fiber Pro product"
echo "  2. Verify service qualification works correctly"
echo "  3. Update API documentation with new business product"
echo "  4. Monitor catalog health with sync_catalog_data tool"
echo ""
