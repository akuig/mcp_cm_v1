#!/bin/bash
# Database verification script to check enhanced schema and data

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

echo "🔍 Enhanced Database Verification"
echo "================================="

# Check if PostgreSQL container is running
if ! docker ps | grep -q telecom_postgres; then
    print_error "PostgreSQL container is not running"
    echo "Start it with: docker-compose -f docker-compose.extended.yml up -d postgres"
    exit 1
fi

print_success "✓ PostgreSQL container is running"

# Check database connectivity
if ! docker exec telecom_postgres pg_isready -U telecom_user -d telecom_catalog &>/dev/null; then
    print_error "Cannot connect to database"
    exit 1
fi

print_success "✓ Database connection established"

# Check enhanced tables
print_status "Checking enhanced table schema..."

enhanced_tables=(
    "service_specifications"
    "product_offerings"
    "offering_service_links"
    "geographic_locations"
    "service_coverage_new"
    "catalog_integrity"
    "sync_operations"
)

basic_tables=(
    "customers"
    "service_coverage"
    "orders"
    "order_addresses"
    "service_activations"
    "activation_addresses"
)

all_enhanced_exist=true
all_basic_exist=true

echo ""
echo "Enhanced Tables:"
echo "---------------"
for table in "${enhanced_tables[@]}"; do
    if docker exec telecom_postgres psql -U telecom_user -d telecom_catalog -tAc "SELECT to_regclass('$table');" | grep -q "^$table$"; then
        print_success "✓ $table"
    else
        print_error "✗ $table (MISSING)"
        all_enhanced_exist=false
    fi
done

echo ""
echo "Basic Tables:"
echo "------------"
for table in "${basic_tables[@]}"; do
    if docker exec telecom_postgres psql -U telecom_user -d telecom_catalog -tAc "SELECT to_regclass('$table');" | grep -q "^$table$"; then
        print_success "✓ $table"
    else
        print_error "✗ $table (MISSING)"
        all_basic_exist=false
    fi
done

# Check data counts
echo ""
echo "Data Verification:"
echo "-----------------"

query_result=$(docker exec telecom_postgres psql -U telecom_user -d telecom_catalog -tAc "
SELECT 
    'customers|' || COALESCE((SELECT COUNT(*) FROM customers), 0) ||
    '|service_specifications|' || COALESCE((SELECT COUNT(*) FROM service_specifications), 0) ||
    '|product_offerings|' || COALESCE((SELECT COUNT(*) FROM product_offerings), 0) ||
    '|offering_service_links|' || COALESCE((SELECT COUNT(*) FROM offering_service_links), 0) ||
    '|geographic_locations|' || COALESCE((SELECT COUNT(*) FROM geographic_locations), 0) ||
    '|service_coverage_new|' || COALESCE((SELECT COUNT(*) FROM service_coverage_new), 0);
")

# Parse the results
IFS='|' read -ra COUNTS <<< "$query_result"
customers_count=${COUNTS[1]}
service_specs_count=${COUNTS[3]}
product_offerings_count=${COUNTS[5]}
links_count=${COUNTS[7]}
geo_locations_count=${COUNTS[9]}
coverage_new_count=${COUNTS[11]}

echo "• Customers: $customers_count"
echo "• Service Specifications: $service_specs_count"
echo "• Product Offerings: $product_offerings_count"
echo "• Offering-Service Links: $links_count"
echo "• Geographic Locations: $geo_locations_count"
echo "• Enhanced Coverage Records: $coverage_new_count"

# Check specific customer data
echo ""
echo "Sample Customer Data:"
echo "--------------------"
docker exec telecom_postgres psql -U telecom_user -d telecom_catalog -c "
SELECT id, name, account_status, credit_score, has_overdue_payments 
FROM customers 
ORDER BY id 
LIMIT 5;
"

# Check sample service specifications
echo ""
echo "Sample Service Specifications:"
echo "-----------------------------"
docker exec telecom_postgres psql -U telecom_user -d telecom_catalog -c "
SELECT id, name, service_type, LEFT(description, 50) as description_preview
FROM service_specifications 
ORDER BY service_type, name 
LIMIT 8;
"

# Check sample product offerings
echo ""
echo "Sample Product Offerings:"
echo "------------------------"
docker exec telecom_postgres psql -U telecom_user -d telecom_catalog -c "
SELECT id, name, category, price_monthly, is_active
FROM product_offerings 
ORDER BY category, price_monthly 
LIMIT 8;
"

# Summary
echo ""
echo "Summary:"
echo "========"

if [ "$all_enhanced_exist" = true ] && [ "$all_basic_exist" = true ]; then
    print_success "✅ All required tables exist"
else
    print_error "❌ Some tables are missing"
fi

if [ "$customers_count" -gt 0 ] && [ "$service_specs_count" -gt 0 ] && [ "$product_offerings_count" -gt 0 ]; then
    print_success "✅ Sample data is present"
else
    print_warning "⚠️  Some sample data may be missing"
fi

if [ "$links_count" -gt 0 ]; then
    print_success "✅ Product-Service links are configured"
else
    print_warning "⚠️  No product-service links found"
fi

if [ "$geo_locations_count" -gt 0 ] && [ "$coverage_new_count" -gt 0 ]; then
    print_success "✅ Geographic coverage data is present"
else
    print_warning "⚠️  Geographic coverage data may be incomplete"
fi

echo ""
if [ "$all_enhanced_exist" = true ] && [ "$customers_count" -gt 0 ] && [ "$service_specs_count" -gt 0 ]; then
    print_success "🎉 Enhanced database verification PASSED!"
    echo ""
    echo "You can now:"
    echo "• Start services: make enhanced-up"
    echo "• Test MCP tools: make enhanced-test"
    echo "• Access APIs at: http://localhost:8080"
else
    print_error "❌ Enhanced database verification FAILED!"
    echo ""
    echo "To fix this:"
    echo "• Run: ./reset_db_enhanced.sh"
    echo "• Or: make enhanced-deploy"
fi
