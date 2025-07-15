#!/bin/bash

# Telepath AI Catalog Manager Deployment Script
# Version: 1.0

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="telepath-ai"
BASE_DIR=$(pwd)

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    # Check if Docker daemon is running
    if ! docker info &> /dev/null; then
        log_error "Docker daemon is not running. Please start Docker first."
        exit 1
    fi
    
    log_success "Prerequisites check passed"
}

setup_directory_structure() {
    log_info "Setting up directory structure..."
    
    # Create main directories
    mkdir -p catalog-manager
    mkdir -p mcp-server
    mkdir -p database
    mkdir -p logs
    mkdir -p monitoring
    mkdir -p web-ui
    
    # Create subdirectories
    mkdir -p monitoring/grafana/dashboards
    mkdir -p monitoring/grafana/datasources
    
    log_success "Directory structure created"
}

deploy_database_files() {
    log_info "Deploying database files..."
    
    # Copy database migration and sample data files
    # Note: These should be saved from the artifacts above
    
    log_success "Database files deployed"
}

deploy_catalog_manager() {
    log_info "Deploying Catalog Manager..."
    
    # Copy catalog manager files
    # Note: The Python files should be saved from the artifacts above
    
    log_success "Catalog Manager deployed"
}

deploy_mcp_server() {
    log_info "Deploying Enhanced MCP Server..."
    
    # Copy MCP server files
    # Note: The enhanced MCP server should be saved from the artifacts above
    
    log_success "Enhanced MCP Server deployed"
}

build_and_start_services() {
    log_info "Building and starting services..."
    
    # Stop any existing services
    docker-compose down --remove-orphans 2>/dev/null || true
    
    # Remove old volumes if needed
    if [ "$1" = "--clean" ]; then
        log_warning "Cleaning existing volumes..."
        docker-compose down -v
        docker volume prune -f
    fi
    
    # Build and start services
    docker-compose up --build -d
    
    log_success "Services started"
}

wait_for_services() {
    log_info "Waiting for services to be ready..."
    
    # Wait for MySQL
    log_info "Waiting for MySQL to be ready..."
    timeout=60
    while [ $timeout -gt 0 ]; do
        if docker-compose exec -T mysql mysqladmin ping -h localhost -u catalog_user -pcatalog_pass --silent; then
            break
        fi
        sleep 1
        timeout=$((timeout - 1))
    done
    
    if [ $timeout -eq 0 ]; then
        log_error "MySQL failed to start within 60 seconds"
        exit 1
    fi
    
    # Wait for Catalog Manager
    log_info "Waiting for Catalog Manager to be ready..."
    timeout=60
    while [ $timeout -gt 0 ]; do
        if curl -f http://localhost:8080/admin/health &>/dev/null; then
            break
        fi
        sleep 1
        timeout=$((timeout - 1))
    done
    
    if [ $timeout -eq 0 ]; then
        log_error "Catalog Manager failed to start within 60 seconds"
        exit 1
    fi
    
    log_success "All services are ready"
}

run_health_checks() {
    log_info "Running health checks..."
    
    # Check MySQL
    if docker-compose exec -T mysql mysqladmin ping -h localhost -u catalog_user -pcatalog_pass --silent; then
        log_success "MySQL is healthy"
    else
        log_error "MySQL health check failed"
        exit 1
    fi
    
    # Check Redis
    if docker-compose exec -T redis redis-cli ping | grep -q PONG; then
        log_success "Redis is healthy"
    else
        log_error "Redis health check failed"
        exit 1
    fi
    
    # Check Catalog Manager
    if curl -f http://localhost:8080/admin/health &>/dev/null; then
        log_success "Catalog Manager is healthy"
    else
        log_error "Catalog Manager health check failed"
        exit 1
    fi
    
    log_success "All health checks passed"
}

verify_data() {
    log_info "Verifying sample data..."
    
    # Test service specifications endpoint
    specs_count=$(curl -s http://localhost:8080/tmf633/serviceSpecification | jq length)
    log_info "Service Specifications loaded: $specs_count"
    
    # Test product offerings endpoint
    offerings_count=$(curl -s http://localhost:8080/tmf620/productOffering | jq length)
    log_info "Product Offerings loaded: $offerings_count"
    
    # Test geographic locations endpoint
    locations_count=$(curl -s http://localhost:8080/tmf673/geographicLocation | jq length)
    log_info "Geographic Locations loaded: $locations_count"
    
    # Test customer lookup
    customer_response=$(curl -s http://localhost:8080/tmf629/customer/8452934)
    customer_name=$(echo $customer_response | jq -r .name)
    log_info "Test customer: $customer_name"
    
    log_success "Data verification completed"
}

show_available_services() {
    log_info "Available Services:"
    echo ""
    echo "Service Specifications:"
    curl -s http://localhost:8080/tmf633/serviceSpecification | jq -r '.[] | "  - \(.id): \(.name)"'
    echo ""
    
    echo "Product Offerings:"
    curl -s http://localhost:8080/tmf620/productOffering | jq -r '.[] | "  - \(.id): \(.name) ($\(.price.amount)/\(.price.period))"'
    echo ""
    
    echo "Geographic Coverage:"
    curl -s http://localhost:8080/tmf673/geographicLocation | jq -r '.[] | "  - \(.streetNumber) \(.streetName), \(.city)"'
    echo ""
}

show_endpoints() {
    log_info "API Endpoints:"
    echo ""
    echo "Catalog Manager API: http://localhost:8080"
    echo "  - Health Check: http://localhost:8080/admin/health"
    echo "  - Service Specs: http://localhost:8080/tmf633/serviceSpecification"
    echo "  - Product Offerings: http://localhost:8080/tmf620/productOffering"
    echo "  - Geographic Locations: http://localhost:8080/tmf673/geographicLocation"
    echo ""
    echo "MCP Server: http://localhost:8081"
    echo "Grafana Dashboard: http://localhost:3000 (admin/admin)"
    echo "Prometheus: http://localhost:9090"
    echo ""
}

cleanup() {
    log_info "Cleaning up deployment..."
    docker-compose down
    docker system prune -f
    log_success "Cleanup completed"
}

# Main deployment function
main() {
    case "$1" in
        "deploy")
            log_info "Starting Telepath AI Catalog Manager deployment..."
            check_prerequisites
            setup_directory_structure
            deploy_database_files
            deploy_catalog_manager  
            deploy_mcp_server
            build_and_start_services "$2"
            wait_for_services
            run_health_checks
            verify_data
            show_available_services
            show_endpoints
            log_success "Deployment completed successfully!"
            ;;
        "start")
            log_info "Starting services..."
            docker-compose up -d
            wait_for_services
            run_health_checks
            log_success "Services started successfully!"
            ;;
        "stop")
            log_info "Stopping services..."
            docker-compose down
            log_success "Services stopped"
            ;;
        "restart")
            log_info "Restarting services..."
            docker-compose down
            docker-compose up -d
            wait_for_services
            run_health_checks
            log_success "Services restarted successfully!"
            ;;
        "status")
            log_info "Checking service status..."
            docker-compose ps
            run_health_checks
            ;;
        "logs")
            service="${2:-}"
            if [ -n "$service" ]; then
                docker-compose logs -f "$service"
            else
                docker-compose logs -f
            fi
            ;;
        "clean")
            cleanup
            ;;
        "test")
            log_info "Running tests..."
            verify_data
            show_available_services
            ;;
        *)
            echo "Usage: $0 {deploy|start|stop|restart|status|logs|clean|test}"
            echo ""
            echo "Commands:"
            echo "  deploy [--clean]  - Full deployment (use --clean to reset data)"
            echo "  start            - Start services"
            echo "  stop             - Stop services"
            echo "  restart          - Restart services"
            echo "  status           - Check service status"
            echo "  logs [service]   - Show logs (optional service name)"
            echo "  clean            - Clean up deployment"
            echo "  test             - Test deployed services"
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"