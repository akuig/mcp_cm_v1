#!/bin/bash
# Quickest way to apply the fix - uses Docker exec

echo "Applying product_service_links fix..."
echo ""

# Copy SQL to container and execute it
docker cp create_product_service_links.sql telecom_postgres:/tmp/ && \
docker exec telecom_postgres psql -U telecom_user -d telecom_catalog -f /tmp/create_product_service_links.sql && \
docker exec telecom_postgres rm /tmp/create_product_service_links.sql

if [ $? -eq 0 ]; then
    echo ""
    echo "✓ Done! The product_service_links table has been created."
else
    echo ""
    echo "❌ Error occurred. Make sure 'docker-compose up -d' is running first."
fi
