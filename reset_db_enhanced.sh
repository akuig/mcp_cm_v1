#!/bin/bash
# Enhanced Database Reset Script - Uses full enhanced schema

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

print_status "🔄 Resetting Enhanced Telecom Database..."

# Stop enhanced services
print_status "Stopping enhanced services..."
docker-compose -f docker-compose.extended.yml down 2>/dev/null || true

# Remove old postgres data volume
print_status "Removing old database volume..."
docker volume rm mcp_cm_v1_postgres_data 2>/dev/null || true

# Start only postgres with enhanced configuration
print_status "Starting PostgreSQL with enhanced schema..."
docker-compose -f docker-compose.extended.yml up -d postgres

# Wait for postgres to be ready
print_status "Waiting for PostgreSQL to initialize..."
max_attempts=30
attempt=0

while [ $attempt -lt $max_attempts ]; do
    attempt=$((attempt + 1))
    if docker exec telecom_postgres pg_isready -U telecom_user -d telecom_catalog &>/dev/null; then
        print_success "✓ PostgreSQL is ready"
        break
    fi
    
    if [ $attempt -eq $max_attempts ]; then
        print_error "PostgreSQL failed to start after $max_attempts attempts"
        exit 1
    fi
    
    sleep 2
done

# Additional wait for initialization to complete
sleep 5

# Verify the enhanced schema was created
print_status "Verifying enhanced database schema..."

# Check if key enhanced tables exist
tables_to_check=(
    "service_specifications"
    "product_offerings" 
    "offering_service_links"
    "geographic_locations"
    "service_coverage_new"
    "catalog_integrity"
    "sync_operations"
)

all_tables_exist=true

for table in "${tables_to_check[@]}"; do
    if docker exec telecom_postgres psql -U telecom_user -d telecom_catalog -tAc "SELECT to_regclass('$table');" | grep -q "^$table$"; then
        print_success "✓ Table '$table' exists"
    else
        print_error "✗ Table '$table' missing"
        all_tables_exist=false
    fi
done

if [ "$all_tables_exist" = false ]; then
    print_error "Some enhanced tables are missing. Re-running initialization..."
    
    # Force re-run the initialization script
    print_status "Running enhanced database initialization manually..."
    docker exec -i telecom_postgres psql -U telecom_user -d telecom_catalog < init_db_extended.sql
    
    # Re-check tables
    print_status "Re-verifying tables..."
    for table in "${tables_to_check[@]}"; do
        if docker exec telecom_postgres psql -U telecom_user -d telecom_catalog -tAc "SELECT to_regclass('$table');" | grep -q "^$table$"; then
            print_success "✓ Table '$table' now exists"
        else
            print_error "✗ Table '$table' still missing"
        fi
    done
fi

# Verify data was inserted
print_status "Verifying sample data..."

record_counts=$(docker exec telecom_postgres psql -U telecom_user -d telecom_catalog -tAc "
SELECT 
    (SELECT COUNT(*) FROM customers) as customers,
    (SELECT COUNT(*) FROM service_specifications) as service_specs,
    (SELECT COUNT(*) FROM product_offerings) as product_offerings,
    (SELECT COUNT(*) FROM geographic_locations) as geo_locations,
    (SELECT COUNT(*) FROM service_coverage_new) as coverage_new;
")

echo "Record counts: $record_counts"

customer_count=$(echo $record_counts | cut -d'|' -f1)
service_spec_count=$(echo $record_counts | cut -d'|' -f2)
offering_count=$(echo $record_counts | cut -d'|' -f3)
geo_count=$(echo $record_counts | cut -d'|' -f4)
coverage_count=$(echo $record_counts | cut -d'|' -f5)

print_success "✓ Customers: $customer_count"
print_success "✓ Service Specifications: $service_spec_count" 
print_success "✓ Product Offerings: $offering_count"
print_success "✓ Geographic Locations: $geo_count"
print_success "✓ Enhanced Coverage Records: $coverage_count"

print_success "🎉 Enhanced database reset completed successfully!"

echo ""
echo "Next steps:"
echo "1. Start all services: make enhanced-up"
echo "2. Test functionality: make enhanced-test"
echo "3. Open MCP Inspector: make inspector"
echo ""
echo "Available endpoints after starting services:"
echo "• Catalog Manager API: http://localhost:8080"
echo "• MCP Server: http://localhost:8090"
echo "• Database shell: make db-shell"
