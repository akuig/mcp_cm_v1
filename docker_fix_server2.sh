#!/bin/bash
# ================================================================
# EXECUTE SERVER 2 CRITICAL FIX (Fanore MCP)
# Fixes broken business product link and adds coverage
# ================================================================

echo "================================================"
echo "SERVER 2 (Fanore) CRITICAL FIX"
echo "================================================"
echo ""

CONTAINER_NAME="telecom_postgres"
SQL_FILE="fix_server2_critical.sql"

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
echo "Executing critical fix..."
echo "================================================"
echo ""

docker exec -i "$CONTAINER_NAME" psql -U telecom_user -d telecom_catalog -f "/tmp/$SQL_FILE"

EXIT_CODE=$?

# Cleanup
docker exec "$CONTAINER_NAME" rm "/tmp/$SQL_FILE"

echo ""
echo "================================================"

if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ SUCCESS: Server 2 critical fix applied!"
    echo ""
    echo "What was fixed:"
    echo "  ✓ Business product linked to service specification"
    echo "  ✓ Business fiber coverage added to premium locations"
    echo "  ✓ Phone service coverage added to all locations"
    echo "  ✓ Security service coverage added to all locations"
    echo ""
    echo "Next steps:"
    echo "  1. Run standardization: ./docker_standardize_both.sh"
    echo "  2. Test business product ordering"
    echo "  3. Verify coverage with MCP tools"
else
    echo "❌ Error: Fix failed"
    echo ""
    echo "Check error messages above for details"
    exit 1
fi
