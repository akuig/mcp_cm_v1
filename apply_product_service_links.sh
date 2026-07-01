#!/bin/bash
# Script to create and populate the product_service_links table
# This fixes the missing table issue in the catalog manager

echo "================================================"
echo "Creating product_service_links table"
echo "================================================"
echo ""

# Database connection details
DB_USER="telecom_user"
DB_NAME="telecom_catalog"
export PGPASSWORD="telecom_catalog"

# Check if PostgreSQL is running
if ! pg_isready -h localhost -p 5432 > /dev/null 2>&1; then
    echo "❌ Error: PostgreSQL is not running on localhost:5432"
    echo "Please start PostgreSQL first using:"
    echo "  docker-compose up -d postgres"
    echo "  or"
    echo "  pg_ctl start"
    exit 1
fi

echo "✓ PostgreSQL is running"
echo ""

# Check if database exists
if ! psql -h localhost -U "$DB_USER" -lqt | cut -d \| -f 1 | grep -qw "$DB_NAME"; then
    echo "❌ Error: Database '$DB_NAME' does not exist"
    echo "Please create the database first"
    exit 1
fi

echo "✓ Database '$DB_NAME' exists"
echo ""

# Execute the SQL script
echo "Executing SQL script..."
echo ""

if psql -h localhost -U "$DB_USER" -d "$DB_NAME" -f create_product_service_links.sql; then
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
    echo "You can now use the catalog manager tools with full"
    echo "product-to-service mapping functionality."
    echo ""
else
    echo ""
    echo "❌ Error: Failed to execute SQL script"
    echo "Please check the error messages above"
    exit 1
fi

# Unset password
unset PGPASSWORD
