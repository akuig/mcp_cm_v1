#!/bin/bash
# Apply product_service_links fix via localhost connection
# Uses the correct Docker password

echo "================================================"
echo "Creating product_service_links table"
echo "================================================"
echo ""

# Database connection details from docker-compose.yml
DB_USER="telecom_user"
DB_PASS="telecom_pass"  # Correct password from docker-compose.yml
DB_NAME="telecom_catalog"
DB_HOST="localhost"
DB_PORT="5432"

export PGPASSWORD="$DB_PASS"

# Check if PostgreSQL is accessible
if ! pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" > /dev/null 2>&1; then
    echo "❌ Error: Cannot connect to PostgreSQL at $DB_HOST:$DB_PORT"
    echo ""
    echo "Make sure Docker containers are running:"
    echo "  docker-compose up -d"
    echo ""
    echo "If containers are running, use the Docker script instead:"
    echo "  ./docker_fix_links.sh"
    exit 1
fi

echo "✓ PostgreSQL is accessible"
echo ""

# Execute the SQL script
echo "Executing SQL script..."
echo ""

if psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -f create_product_service_links.sql; then
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
else
    echo ""
    echo "❌ Error: Failed to execute SQL script"
    echo ""
    echo "If you see authentication errors, try the Docker method:"
    echo "  ./docker_fix_links.sh"
    exit 1
fi

# Unset password
unset PGPASSWORD
