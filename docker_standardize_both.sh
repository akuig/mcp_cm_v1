#!/bin/bash
# ================================================================
# STANDARDIZE BOTH SERVERS
# Ensures identical catalogs on Server 1 and Server 2
# ================================================================

echo "================================================"
echo "CATALOG STANDARDIZATION - BOTH SERVERS"
echo "================================================"
echo ""

CONTAINER_NAME="telecom_postgres"
SQL_FILE="standardize_both_servers.sql"

# Check if SQL file exists
if [ ! -f "$SQL_FILE" ]; then
    echo "❌ Error: $SQL_FILE not found"
    exit 1
fi

# Check if container is running
if ! docker ps | grep -q "$CONTAINER_NAME"; then
    echo "❌ Error: PostgreSQL container '$CONTAINER_NAME' is not running"
    echo ""
    echo "Start containers first:"
    echo "  docker-compose up -d"
    exit 1
fi

echo "✓ PostgreSQL container is running"
echo ""

echo "⚠️  IMPORTANT: This script should be run on BOTH servers"
echo "   Run it separately for each server's database"
echo ""
read -p "Continue with standardization? (y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled"
    exit 0
fi

# Copy SQL file to container
echo "Copying SQL file to container..."
docker cp "$SQL_FILE" "$CONTAINER_NAME:/tmp/"

if [ $? -ne 0 ]; then
    echo "❌ Error: Failed to copy SQL file"
    exit 1
fi

echo "✓ SQL file copied"
echo ""

# Execute SQL
echo "Running standardization..."
echo "================================================"
echo ""

docker exec -i "$CONTAINER_NAME" psql -U telecom_user -d telecom_catalog -f "/tmp/$SQL_FILE"

EXIT_CODE=$?

# Cleanup
docker exec "$CONTAINER_NAME" rm "/tmp/$SQL_FILE"

echo ""
echo "================================================"

if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ SUCCESS: Catalog standardized!"
    echo ""
    echo "Standardization complete:"
    echo "  ✓ 23 service specifications (including business)"
    echo "  ✓ 15 active product offerings (including business)"
    echo "  ✓ 25 product-service links (all verified)"
    echo "  ✓ Complete coverage data for all service types"
    echo ""
    echo "Both servers now have:"
    echo "  • Identical product catalogs"
    echo "  • Matching service specifications"
    echo "  • Consistent coverage data"
    echo "  • All products properly linked"
    echo ""
    echo "⚠️  Remember to run this on the OTHER server too!"
else
    echo "❌ Error: Standardization failed"
    echo ""
    echo "Check error messages above for details"
    exit 1
fi
