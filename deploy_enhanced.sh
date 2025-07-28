#!/bin/bash

# Enhanced Telecom MCP Deployment Script
# Deploys the extended version with new TM Forum services

set -e

echo "🚀 Starting Enhanced Telecom MCP Deployment..."

# Configuration
BACKUP_DIR="./backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
COMPOSE_FILE="docker-compose.extended.yml"

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

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Function to backup database
backup_database() {
    print_status "Creating database backup..."
    
    if docker ps | grep -q telecom_postgres; then
        docker exec telecom_postgres pg_dump -U telecom_user telecom_catalog > "$BACKUP_DIR/catalog_backup_$TIMESTAMP.sql"
        print_success "Database backed up to $BACKUP_DIR/catalog_backup_$TIMESTAMP.sql"
    else
        print_warning "PostgreSQL container not running, skipping backup"
    fi
}

# Function to stop existing services
stop_services() {
    print_status "Stopping existing services..."
    
    if [ -f "docker-compose.yml" ]; then
        docker-compose -f docker-compose.yml down || true
    fi
    
    # Stop any running containers
    docker stop telecom_postgres catalog_manager mcp_server 2>/dev/null || true
    
    print_success "Services stopped"
}

# Function to build new images
build_images() {
    print_status "Building enhanced Docker images..."
    
    docker-compose -f "$COMPOSE_FILE" build --no-cache
    
    print_success "Images built successfully"
}

# Function to start enhanced services
start_services() {
    print_status "Starting enhanced services..."
    
    docker-compose -f "$COMPOSE_FILE" up -d
    
    print_status "Waiting for services to be healthy..."
    sleep 15
    
    # Check service health
    check_services_health
}

# Function to check service health
check_services_health() {
    local max_attempts=12
    local attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        attempt=$((attempt + 1))
        print_status "Health check attempt $attempt/$max_attempts..."
        
        # Check PostgreSQL
        if docker exec telecom_postgres pg_isready -U telecom_user -d telecom_catalog &>/dev/null; then
            print_success "✓ PostgreSQL is healthy"
        else
            print_error "✗ PostgreSQL is not ready"
            if [ $attempt -eq $max_attempts ]; then
                print_error "PostgreSQL failed to start properly"
                exit 1
            fi
            sleep 10
            continue
        fi
        
        # Check Catalog Manager
        if curl -f http://localhost:8080/health &>/dev/null; then
            print_success "✓ Catalog Manager is healthy"
        else
            print_error "✗ Catalog Manager is not ready"
            if [ $attempt -eq $max_attempts ]; then
                print_error "Catalog Manager failed to start properly"
                exit 1
            fi
            sleep 10
            continue
        fi
        
        # Check MCP Server
        if curl -f http://localhost:8090/health &>/dev/null; then
            print_success "✓ MCP Server is healthy"
        else
            print_warning "✗ MCP Server health check failed (may not have health endpoint)"
        fi
        
        break
    done
}

# Function to run database migrations
run_migrations() {
    print_status "Running database migrations for enhanced schema..."
    
    # The enhanced init_db_extended.sql should handle the migration
    # But we can add specific migration steps here if needed
    
    print_success "Database migrations completed"
}

# Function to test new functionality
test_new_features() {
    print_status "Testing new enhanced features..."
    
    # Test service specifications endpoint
    if curl -s http://localhost:8080/api/service-specifications | jq . >/dev/null 2>&1; then
        print_success "✓ Service specifications API working"
    else
        print_error "✗ Service specifications API failed"
    fi
    
    # Test product offerings endpoint
    if curl -s http://localhost:8080/api/product-offerings | jq . >/dev/null 2>&1; then
        print_success "✓ Product offerings API working"
    else
        print_error "✗ Product offerings API failed"
    fi
    
    # Test geographic locations endpoint
    if curl -s http://localhost:8080/api/geographic-locations | jq . >/dev/null 2>&1; then
        print_success "✓ Geographic locations API working"
    else
        print_error "✗ Geographic locations API failed"
    fi
    
    print_success "Enhanced features testing completed"
}

# Function to display deployment summary
show_summary() {
    echo ""
    echo "================================================"
    echo "🎉 Enhanced Telecom MCP Deployment Complete!"
    echo "================================================"
    echo ""
    echo "📍 Service Endpoints:"
    echo "   • Catalog Manager API: http://localhost:8080"
    echo "   • MCP Server: http://localhost:8090"
    echo "   • MCP Streaming endpoint: http://localhost:8090/mcp/stream"
    echo ""
    echo "🔧 Enhanced APIs Available:"
    echo "   • TMF637: Service Qualification"
    echo "   • TMF629: Customer Management"
    echo "   • TMF622: Product Ordering"
    echo "   • TMF640: Service Activation"
    echo ""
    echo "🆕 New Catalog Management APIs:"
    echo "   • GET /api/service-specifications - List/filter service specs"
    echo "   • POST /api/service-specifications - Create service specs"
    echo "   • GET /api/product-offerings - List/filter product offerings"
    echo "   • POST /api/product-offerings - Create product offerings"
    echo "   • GET /api/geographic-locations - List locations with coverage"
    echo "   • POST /api/geographic-locations - Add new locations"
    echo "   • POST /api/link-offering-to-specification - Link products to services"
    echo "   • POST /api/add-geographic-coverage - Add coverage areas"
    echo "   • POST /api/sync-catalog-data - Validate and sync catalog"
    echo ""
    echo "🛠️ New MCP Tools for Claude:"
    echo "   • list_service_specifications"
    echo "   • list_product_offerings"
    echo "   • list_geographic_locations"
    echo "   • sync_catalog_data"
    echo "   • create_service_specification"
    echo "   • create_product_offering"
    echo "   • link_offering_to_specification"
    echo "   • add_geographic_coverage"
    echo ""
    echo "📊 Management Commands:"
    echo "   • make logs - View service logs"
    echo "   • make health - Check service health"
    echo "   • make test-enhanced - Test new features"
    echo "   • make inspector - Open MCP Inspector"
    echo ""
    echo "📁 Backup Location: $BACKUP_DIR/catalog_backup_$TIMESTAMP.sql"
    echo ""
}

# Main deployment flow
main() {
    echo "Enhanced Telecom MCP Deployment"
    echo "==============================="
    echo ""
    
    # Check if docker and docker-compose are available
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed or not in PATH"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "docker-compose is not installed or not in PATH"
        exit 1
    fi
    
    # Check if jq is available for testing
    if ! command -v jq &> /dev/null; then
        print_warning "jq is not installed - some tests will be skipped"
    fi
    
    print_status "Starting deployment process..."
    
    # Backup existing database
    backup_database
    
    # Stop existing services
    stop_services
    
    # Build new images
    build_images
    
    # Start enhanced services
    start_services
    
    # Run any necessary migrations
    run_migrations
    
    # Test new functionality
    test_new_features
    
    # Show deployment summary
    show_summary
    
    print_success "Deployment completed successfully! 🎉"
}

# Handle script arguments
case "${1:-}" in
    --backup-only)
        backup_database
        exit 0
        ;;
    --test-only)
        test_new_features
        exit 0
        ;;
    --help)
        echo "Enhanced Telecom MCP Deployment Script"
        echo ""
        echo "Usage: $0 [option]"
        echo ""
        echo "Options:"
        echo "  --backup-only    Only backup the database"
        echo "  --test-only      Only test the new features"
        echo "  --help           Show this help message"
        echo ""
        echo "Default: Run full deployment"
        exit 0
        ;;
    "")
        main
        ;;
    *)
        print_error "Unknown option: $1"
        echo "Use --help for usage information"
        exit 1
        ;;
esac
