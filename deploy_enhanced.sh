#!/bin/bash

# Complete deployment script for Enhanced Catalog Manager
# This script handles all deployment scenarios

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Print banner
echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════════════╗"
echo "║     Telepath Enhanced Catalog Manager Deployment     ║"
echo "╚══════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Function to print colored messages
print_info() { echo -e "${BLUE}ℹ${NC} $1"; }
print_success() { echo -e "${GREEN}✓${NC} $1"; }
print_warning() { echo -e "${YELLOW}⚠${NC} $1"; }
print_error() { echo -e "${RED}✗${NC} $1"; }

# Function to check prerequisites
check_prerequisites() {
    echo -e "\n${YELLOW}Checking prerequisites...${NC}"
    
    local all_good=true
    
    # Check Docker
    if command -v docker &> /dev/null; then
        print_success "Docker installed: $(docker --version)"
    else
        print_error "Docker not installed"
        all_good=false
    fi
    
    # Check Docker Compose
    if command -v docker-compose &> /dev/null; then
        print_success "Docker Compose installed: $(docker-compose --version)"
    else
        print_warning "Docker Compose not installed (optional)"
    fi
    
    # Check Python
    if command -v python3 &> /dev/null; then
        print_success "Python3 installed: $(python3 --version)"
    else
        print_warning "Python3 not installed (needed for diagnostics)"
    fi
    
    # Check required files
    echo -e "\n${YELLOW}Checking required files...${NC}"
    
    local required_files=("catalog_manager_enhanced.py" "mcp_server.py" "Dockerfile" "requirements.txt")
    for file in "${required_files[@]}"; do
        if [ -f "$file" ]; then
            print_success "Found: $file"
        else
            print_error "Missing: $file"
            all_good=false
        fi
    done
    
    if [ "$all_good" = false ]; then
        print_error "Prerequisites check failed. Please ensure all requirements are met."
        exit 1
    fi
}

# Function to stop existing services
stop_existing_services() {
    echo -e "\n${YELLOW}Stopping existing services...${NC}"
    
    # Stop catalog manager
    if docker ps | grep -q catalog_manager; then
        docker stop catalog_manager 2>/dev/null || true
        docker rm catalog_manager 2>/dev/null || true
        print_success "Stopped existing catalog manager"
    fi
    
    # Stop MCP server
    if docker ps | grep -q mcp_server; then
        docker stop mcp_server 2>/dev/null || true
        docker rm mcp_server 2>/dev/null || true
        print_success "Stopped existing MCP server"
    fi
}

# Function to build images
build_images() {
    echo -e "\n${YELLOW}Building Docker images...${NC}"
    
    # Build catalog manager
    print_info "Building catalog-manager image..."
    if docker build -t catalog-manager:latest -f Dockerfile . > /dev/null 2>&1; then
        print_success "Built catalog-manager:latest"
    else
        print_error "Failed to build catalog-manager image"
        exit 1
    fi
}

# Function to deploy with docker-compose
deploy_with_compose() {
    echo -e "\n${YELLOW}Deploying with Docker Compose...${NC}"
    
    local compose_file=$1
    
    print_info "Using compose file: $compose_file"
    
    if docker-compose -f "$compose_file" up -d; then
        print_success "Services deployed successfully"
    else
        print_error "Failed to deploy services"
        exit 1
    fi
}

# Function to deploy standalone
deploy_standalone() {
    echo -e "\n${YELLOW}Deploying standalone catalog manager...${NC}"
    
    docker run -d \
        --name catalog_manager \
        -p 8080:8080 \
        -v "$(pwd)/catalog_manager_enhanced.py:/app/catalog_manager.py:ro" \
        -v "$(pwd)/data:/app/data" \
        --restart unless-stopped \
        catalog-manager:latest
    
    if [ $? -eq 0 ]; then
        print_success "Catalog manager deployed"
    else
        print_error "Failed to deploy catalog manager"
        exit 1
    fi
}

# Function to wait for services
wait_for_services() {
    echo -e "\n${YELLOW}Waiting for services to be ready...${NC}"
    
    local max_attempts=30
    local attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if curl -s http://localhost:8080/health > /dev/null 2>&1; then
            print_success "Catalog manager is ready!"
            return 0
        fi
        
        attempt=$((attempt + 1))
        echo -n "."
        sleep 1
    done
    
    echo ""
    print_error "Services failed to start within 30 seconds"
    return 1
}

# Function to run tests
run_tests() {
    echo -e "\n${YELLOW}Running endpoint tests...${NC}"
    
    if [ -f "quick_test.py" ]; then
        python3 quick_test.py http://localhost:8080
    else
        # Basic curl tests
        print_info "Running basic tests..."
        
        # Health check
        if curl -s http://localhost:8080/health | grep -q "healthy"; then
            print_success "Health check passed"
        else
            print_error "Health check failed"
        fi
        
        # API info
        if curl -s http://localhost:8080/api | grep -q "Telepath"; then
            print_success "API info endpoint working"
        else
            print_error "API info endpoint not working"
        fi
        
        # Service specifications
        if curl -s http://localhost:8080/api/service-specifications | grep -q "serviceSpecifications"; then
            print_success "Service specifications endpoint working"
        else
            print_error "Service specifications endpoint not working"
        fi
    fi
}

# Function to display information
display_info() {
    echo -e "\n${GREEN}════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}           Deployment Complete!${NC}"
    echo -e "${GREEN}════════════════════════════════════════════════════════${NC}"
    
    echo -e "\n${YELLOW}Service Information:${NC}"
    echo "  • Catalog Manager: http://localhost:8080"
    echo "  • Health Check:    http://localhost:8080/health"
    echo "  • API Info:        http://localhost:8080/api"
    
    echo -e "\n${YELLOW}Available Endpoints:${NC}"
    echo "  Core TMF APIs:"
    echo "    • POST /tmf637/serviceQualification"
    echo "    • GET  /tmf629/customer/{id}"
    echo "    • POST /tmf622/productOrder"
    echo "    • POST /tmf640/serviceActivation"
    
    echo "  Enhanced Catalog APIs:"
    echo "    • GET/POST /api/service-specifications"
    echo "    • GET/POST /api/product-offerings"
    echo "    • GET      /api/geographic-locations"
    echo "    • GET      /api/orders"
    echo "    • POST     /api/sync"
    
    echo -e "\n${YELLOW}Useful Commands:${NC}"
    echo "  • View logs:       docker logs -f catalog_manager"
    echo "  • Stop service:    docker stop catalog_manager"
    echo "  • Run diagnostics: python3 catalog_diagnostics.py http://localhost:8080"
    echo "  • Use with ngrok:  ngrok http 8080"
}

# Main execution
main() {
    # Parse arguments
    local deployment_type="standalone"
    
    if [ "$1" = "--compose" ]; then
        deployment_type="compose-simple"
    elif [ "$1" = "--compose-full" ]; then
        deployment_type="compose-full"
    elif [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
        echo "Usage: $0 [OPTIONS]"
        echo ""
        echo "Options:"
        echo "  --compose       Deploy with docker-compose (simple, in-memory)"
        echo "  --compose-full  Deploy with docker-compose (with PostgreSQL)"
        echo "  --help, -h      Show this help message"
        echo ""
        echo "Default: Deploy standalone catalog manager"
        exit 0
    fi
    
    # Run deployment steps
    check_prerequisites
    stop_existing_services
    build_images
    
    case $deployment_type in
        compose-simple)
            deploy_with_compose "docker-compose.simple.yml"
            ;;
        compose-full)
            deploy_with_compose "docker-compose.enhanced.yml"
            ;;
        *)
            deploy_standalone
            ;;
    esac
    
    wait_for_services
    run_tests
    display_info
    
    echo -e "\n${GREEN}✨ Deployment successful! ✨${NC}\n"
}

# Run main function
main "$@"
