#!/bin/bash
# Apply product_service_links fix using Docker exec
# This runs the SQL directly inside the Docker container

echo "================================================"
echo "Creating product_service_links table (Docker)"
echo "================================================"
echo ""

# Check if container is running
if ! docker ps | grep -q telecom_postgres; then
    echo "❌ Error: PostgreSQL container 'telecom_postgres' is not running"
    echo ""
    echo "Please start the containers first:"
    echo "  docker-compose up -d"
    exit 1
fi

echo "✓ PostgreSQL container is running"
echo ""

# Copy SQL file into container
echo "Copying SQL file to container..."
docker cp create_product_service_links.sql telecom_postgres:/tmp/

if [ $? -ne 0 ]; then
    echo "❌ Error: Failed to copy SQL file to container"
    exit 1
fi

echo "✓ SQL file copied to container"
echo ""

# Execute SQL inside container
echo "Executing SQL script inside container..."
echo ""

docker exec -i telecom_postgres psql -U telecom_user -d telecom_catalog -f /tmp/create_product_service_links.sql

if [ $? -eq 0 ]; then
    echo ""
    echo "================================================"
    echo "✓ SUCCESS: product_service_links table created!"
    echo "================================================"
    echo ""
    echo "Summary:"
    echo "  - Table created with proper foreign keys"
    echo "  - 25 product-to-service links inserted"
    echo "  - Indexes created for performance"
    echo ""
    echo "The catalog manager can now properly link"
    echo "products to their service specifications."
    echo ""
else
    echo ""
    echo "❌ Error: Failed to execute SQL script"
    echo "Please check the error messages above"
    exit 1
fi

# Cleanup
docker exec telecom_postgres rm /tmp/create_product_service_links.sql
