#!/bin/bash
# Comprehensive database fix and setup script

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

echo ""
echo "🔧 Enhanced Telecom MCP Database Setup & Fix"
echo "============================================"

# Make scripts executable
print_status "Making scripts executable..."
chmod +x reset_db_enhanced.sh 2>/dev/null || true
chmod +x verify_db_enhanced.sh 2>/dev/null || true
chmod +x deploy_enhanced.sh 2>/dev/null || true
chmod +x reset_db.sh 2>/dev/null || true
chmod +x check_db.sh 2>/dev/null || true
chmod +x fix_db.sh 2>/dev/null || true
print_success "✓ Scripts made executable"

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker and try again."
    exit 1
fi
print_success "✓ Docker is running"

# Check current database state
print_status "Checking current database state..."

if docker ps | grep -q telecom_postgres; then
    print_status "PostgreSQL container is running - checking table status..."
    
    # Check if enhanced tables exist
    missing_tables=()
    tables_to_check=("product_offerings" "offering_service_links" "geographic_locations" "service_coverage_new")
    
    for table in "${tables_to_check[@]}"; do
        if ! docker exec telecom_postgres psql -U telecom_user -d telecom_catalog -tAc "SELECT to_regclass('$table');" 2>/dev/null | grep -q "^$table$"; then
            missing_tables+=("$table")
        fi
    done
    
    if [ ${#missing_tables[@]} -gt 0 ]; then
        print_warning "⚠️  Missing enhanced tables: ${missing_tables[*]}"
        print_status "Need to reset database with enhanced schema..."
        reset_needed=true
    else
        print_success "✓ Enhanced tables exist"
        reset_needed=false
    fi
else
    print_status "PostgreSQL container not running - will start fresh"
    reset_needed=true
fi

# Reset database if needed
if [ "$reset_needed" = true ]; then
    print_status "🔄 Resetting database with enhanced schema..."
    
    # Stop all services
    print_status "Stopping services..."
    docker-compose -f docker-compose.extended.yml down 2>/dev/null || true
    docker-compose down 2>/dev/null || true
    
    # Remove old volumes
    print_status "Removing old database volumes..."
    docker volume rm mcp_cm_v1_postgres_data 2>/dev/null || true
    
    # Start PostgreSQL with enhanced initialization
    print_status "Starting PostgreSQL with enhanced configuration..."
    docker-compose -f docker-compose.extended.yml up -d postgres
    
    # Wait for PostgreSQL to be ready
    print_status "Waiting for PostgreSQL to initialize..."
    max_attempts=60
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
    
    # Additional wait for init scripts to complete
    sleep 5
    
    # Verify enhanced tables were created
    print_status "Verifying enhanced database schema..."
    
    all_tables_exist=true
    for table in "${tables_to_check[@]}"; do
        if docker exec telecom_postgres psql -U telecom_user -d telecom_catalog -tAc "SELECT to_regclass('$table');" 2>/dev/null | grep -q "^$table$"; then
            print_success "✓ Table '$table' exists"
        else
            print_error "✗ Table '$table' missing"
            all_tables_exist=false
        fi
    done
    
    if [ "$all_tables_exist" = false ]; then
        print_warning "Some tables are missing. Re-running initialization manually..."
        
        # Force re-run the initialization script
        if [ -f "init_db_extended.sql" ]; then
            print_status "Running enhanced database initialization manually..."
            docker exec -i telecom_postgres psql -U telecom_user -d telecom_catalog < init_db_extended.sql
            
            # Re-verify tables
            print_status "Re-verifying tables..."
            for table in "${tables_to_check[@]}"; do
                if docker exec telecom_postgres psql -U telecom_user -d telecom_catalog -tAc "SELECT to_regclass('$table');" 2>/dev/null | grep -q "^$table$"; then
                    print_success "✓ Table '$table' now exists"
                else
                    print_error "✗ Table '$table' still missing"
                fi
            done
        else
            print_error "init_db_extended.sql not found"
            exit 1
        fi
    fi
fi

# Verify data
print_status "Verifying sample data..."
data_check=$(docker exec telecom_postgres psql -U telecom_user -d telecom_catalog -tAc "
SELECT 
    (SELECT COUNT(*) FROM customers) as customers,
    (SELECT COUNT(*) FROM service_specifications) as service_specs,
    (SELECT COUNT(*) FROM product_offerings) as product_offerings,
    (SELECT COUNT(*) FROM geographic_locations) as geo_locations;
")

echo "Data counts: $data_check"

# Start enhanced services
print_status "Starting enhanced services..."
docker-compose -f docker-compose.extended.yml up -d

# Wait for services to be ready
print_status "Waiting for services to start..."
sleep 15

# Health checks
print_status "Performing health checks..."

# Check PostgreSQL
if docker exec telecom_postgres pg_isready -U telecom_user -d telecom_catalog &>/dev/null; then
    print_success "✓ PostgreSQL is healthy"
else
    print_error "✗ PostgreSQL health check failed"
fi

# Check Catalog Manager
max_attempts=20
attempt=0
while [ $attempt -lt $max_attempts ]; do
    attempt=$((attempt + 1))
    if curl -f http://localhost:8080/health &>/dev/null; then
        print_success "✓ Catalog Manager is healthy"
        break
    fi
    
    if [ $attempt -eq $max_attempts ]; then
        print_warning "⚠️  Catalog Manager health check failed (may still be starting)"
    else
        sleep 3
    fi
done

# Test enhanced APIs
print_status "Testing enhanced APIs..."

# Test service specifications
if curl -s http://localhost:8080/api/service-specifications | jq . >/dev/null 2>&1; then
    print_success "✓ Service specifications API working"
else
    print_error "✗ Service specifications API failed"
fi

# Test product offerings
if curl -s http://localhost:8080/api/product-offerings | jq . >/dev/null 2>&1; then
    print_success "✓ Product offerings API working"
else
    print_error "✗ Product offerings API failed"
fi

# Test geographic locations
if curl -s http://localhost:8080/api/geographic-locations | jq . >/dev/null 2>&1; then
    print_success "✓ Geographic locations API working"
else
    print_error "✗ Geographic locations API failed"
fi

echo ""
echo "🎉 Database Setup Complete!"
echo "=========================="
echo ""
echo "✅ Services Status:"
echo "   • PostgreSQL: Running with enhanced schema"
echo "   • Catalog Manager: Running at http://localhost:8080"
echo "   • MCP Server: Running at http://localhost:8090"
echo ""
echo "🔧 Available Commands:"
echo "   • make enhanced-test     - Test all functionality"
echo "   • make inspector         - Open MCP Inspector"
echo "   • make db-shell          - Open database shell"
echo "   • ./verify_db_enhanced.sh - Verify database state"
echo ""
echo "📡 Test MCP Tools:"
echo "   The MCP tools should now work properly!"
echo ""
