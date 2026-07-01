#!/bin/bash
# ================================================================
# ADD BUSINESS PRODUCT TO SERVER 1 (MCP Local)
# Backports enterprise offering from Server 2
# ================================================================

echo "================================================"
echo "SERVER 1 (MCP Local) - ADD BUSINESS PRODUCT"
echo "================================================"
echo ""

CONTAINER_NAME="telecom_postgres"
SQL_FILE="add_business_to_server1.sql"

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
echo "Adding business product to Server 1..."
echo "================================================"
echo ""

docker exec -i "$CONTAINER_NAME" psql -U telecom_user -d telecom_catalog -f "/tmp/$SQL_FILE"

EXIT_CODE=$?

# Cleanup
docker exec "$CONTAINER_NAME" rm "/tmp/$SQL_FILE"

echo ""
echo "================================================"

if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ SUCCESS: Business product added to Server 1!"
    echo ""
    echo "What was added:"
    echo "  ✓ Enterprise Fiber 1 Gbps service specification"
    echo "  ✓ TeleCo Business Fiber Pro product ($179.99/mo)"
    echo "  ✓ Product-service link created"
    echo "  ✓ Business fiber coverage added"
    echo ""
    echo "Next steps:"
    echo "  1. Run standardization: ./docker_standardize_both.sh"
    echo "  2. Test business product on Server 1"
else
    echo "❌ Error: Failed to add business product"
    echo ""
    echo "Check error messages above for details"
    exit 1
fi
