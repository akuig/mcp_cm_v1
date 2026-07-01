#!/bin/bash
# ================================================================
# MASTER MIGRATION SCRIPT
# Fixes and standardizes both servers automatically
# ================================================================

set -e  # Exit on any error

echo "================================================================"
echo "CATALOG MIGRATION & STANDARDIZATION - MASTER SCRIPT"
echo "================================================================"
echo ""
echo "This script will:"
echo "  1. Fix Server 2 (Fanore) critical issues"
echo "  2. Add business product to Server 1 (MCP Local)"
echo "  3. Standardize both servers"
echo ""
echo "⚠️  This assumes you are running on Server 2 first,"
echo "    then will need to run on Server 1 separately"
echo ""

read -p "Which server are you on? (1 for MCP Local, 2 for Fanore): " SERVER_CHOICE

if [ "$SERVER_CHOICE" != "1" ] && [ "$SERVER_CHOICE" != "2" ]; then
    echo "❌ Invalid choice. Please enter 1 or 2"
    exit 1
fi

echo ""
echo "Starting migration for Server $SERVER_CHOICE..."
echo ""

# Make all scripts executable
chmod +x docker_fix_server2.sh
chmod +x docker_add_business_server1.sh
chmod +x docker_standardize_both.sh

if [ "$SERVER_CHOICE" == "2" ]; then
    echo "================================================================"
    echo "STEP 1: Fixing Server 2 Critical Issues"
    echo "================================================================"
    ./docker_fix_server2.sh
    
    echo ""
    echo "================================================================"
    echo "STEP 2: Standardizing Server 2"
    echo "================================================================"
    ./docker_standardize_both.sh
    
    echo ""
    echo "================================================================"
    echo "✅ SERVER 2 MIGRATION COMPLETE!"
    echo "================================================================"
    echo ""
    echo "Next steps:"
    echo "  1. Switch to Server 1 (MCP Local)"
    echo "  2. Run this script again and choose option 1"
    echo "  3. Both servers will then be synchronized"
    
elif [ "$SERVER_CHOICE" == "1" ]; then
    echo "================================================================"
    echo "STEP 1: Adding Business Product to Server 1"
    echo "================================================================"
    ./docker_add_business_server1.sh
    
    echo ""
    echo "================================================================"
    echo "STEP 2: Standardizing Server 1"
    echo "================================================================"
    ./docker_standardize_both.sh
    
    echo ""
    echo "================================================================"
    echo "✅ SERVER 1 MIGRATION COMPLETE!"
    echo "================================================================"
    echo ""
    echo "Both servers are now synchronized!"
fi

echo ""
echo "================================================================"
echo "FINAL STATUS"
echo "================================================================"
echo ""
echo "Run these commands to verify:"
echo ""
echo "# Check product count"
echo "docker exec telecom_postgres psql -U telecom_user -d telecom_catalog -c \\"
echo "  'SELECT COUNT(*) FROM product_offerings WHERE is_active = true;'"
echo ""
echo "# Check business product"
echo "docker exec telecom_postgres psql -U telecom_user -d telecom_catalog -c \\"
echo "  'SELECT name, category, price_monthly FROM product_offerings WHERE id = '\"'\"'pkg_enterprise_fiber_1000'\"'\"';'"
echo ""
echo "# Check product-service links"
echo "docker exec telecom_postgres psql -U telecom_user -d telecom_catalog -c \\"
echo "  'SELECT COUNT(*) FROM product_service_links;'"
echo ""
echo "Or use MCP tools:"
echo "  list_product_offerings with include_services=true"
echo ""
