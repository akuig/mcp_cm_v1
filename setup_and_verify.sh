#!/bin/bash

# Setup and verification script for Telepath Enhanced Catalog Manager
# Run this to ensure everything is properly configured

set -e

echo "================================================"
echo "Telepath Catalog Manager Setup & Verification"
echo "================================================"
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓${NC} $2"
    else
        echo -e "${RED}✗${NC} $2"
    fi
}

# Function to print section headers
print_header() {
    echo ""
    echo -e "${YELLOW}$1${NC}"
    echo "----------------------------------------"
}

# 1. Check Docker installation
print_header "1. Checking Docker Installation"
if command -v docker &> /dev/null; then
    print_status 0 "Docker is installed: $(docker --version)"
else
    print_status 1 "Docker is not installed"
    exit 1
fi

if command -v docker-compose &> /dev/null; then
    print_status 0 "Docker Compose is installed: $(docker-compose --version)"
else
    print_status 1 "Docker Compose is not installed"
fi

# 2. Check for required files
print_header "2. Checking Required Files"

required_files=(
    "catalog_manager_enhanced.py"
    "mcp_server.py"
    "requirements.txt"
    "Dockerfile"
)

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        print_status 0 "Found: $file"
    else
        print_status 1 "Missing: $file"
        echo "   Creating placeholder for $file..."
        touch "$file"
    fi
done

# 3. Build Docker image
print_header "3. Building Docker Image"

echo "Building catalog-manager image..."
docker build -t catalog-manager:latest . 2>&1 | tail -5

if [ $? -eq 0 ]; then
    print_status 0 "Docker image built successfully"
else
    print_status 1 "Docker image build failed"
    exit 1
fi

# 4. Stop any existing containers
print_header "4. Cleaning Up Existing Containers"

if docker ps -a | grep -q catalog-manager; then
    echo "Stopping existing catalog-manager container..."
    docker stop catalog-manager 2>/dev/null || true
    docker rm catalog-manager 2>/dev/null || true
    print_status 0 "Cleaned up existing containers"
else
    print_status 0 "No existing containers to clean"
fi

# 5. Start the catalog manager
print_header "5. Starting Catalog Manager"

echo "Starting catalog-manager container..."
docker run -d \
    --name catalog-manager \
    -p 8080:8080 \
    --restart unless-stopped \
    catalog-manager:latest

if [ $? -eq 0 ]; then
    print_status 0 "Catalog manager started"
else
    print_status 1 "Failed to start catalog manager"
    exit 1
fi

# 6. Wait for service to be ready
print_header "6. Waiting for Service to Initialize"

echo "Waiting for catalog manager to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:8080/health > /dev/null 2>&1; then
        print_status 0 "Service is ready!"
        break
    fi
    if [ $i -eq 30 ]; then
        print_status 1 "Service failed to start within 30 seconds"
        echo "Checking logs..."
        docker logs catalog-manager | tail -20
        exit 1
    fi
    echo -n "."
    sleep 1
done
echo ""

# 7. Test endpoints
print_header "7. Testing API Endpoints"

# Test health endpoint
echo "Testing health endpoint..."
if curl -s http://localhost:8080/health | grep -q "healthy"; then
    print_status 0 "Health check passed"
else
    print_status 1 "Health check failed"
fi

# Test API info endpoint
echo "Testing API info endpoint..."
if curl -s http://localhost:8080/api | grep -q "Telepath Catalog Manager"; then
    print_status 0 "API info endpoint working"
else
    print_status 1 "API info endpoint not working"
fi

# Test service specifications endpoint
echo "Testing service specifications endpoint..."
response=$(curl -s -w "\n%{http_code}" http://localhost:8080/api/service-specifications)
http_code=$(echo "$response" | tail -1)
if [ "$http_code" = "200" ]; then
    print_status 0 "Service specifications endpoint working (HTTP 200)"
else
    print_status 1 "Service specifications endpoint failed (HTTP $http_code)"
fi

# Test product offerings endpoint
echo "Testing product offerings endpoint..."
response=$(curl -s -w "\n%{http_code}" http://localhost:8080/api/product-offerings)
http_code=$(echo "$response" | tail -1)
if [ "$http_code" = "200" ]; then
    print_status 0 "Product offerings endpoint working (HTTP 200)"
else
    print_status 1 "Product offerings endpoint failed (HTTP $http_code)"
fi

# Test geographic locations endpoint
echo "Testing geographic locations endpoint..."
response=$(curl -s -w "\n%{http_code}" http://localhost:8080/api/geographic-locations)
http_code=$(echo "$response" | tail -1)
if [ "$http_code" = "200" ]; then
    print_status 0 "Geographic locations endpoint working (HTTP 200)"
else
    print_status 1 "Geographic locations endpoint failed (HTTP $http_code)"
fi

# 8. Display service information
print_header "8. Service Information"

echo "Catalog Manager is running at: http://localhost:8080"
echo ""
echo "Available endpoints:"
echo "  Core TMF APIs:"
echo "    - POST http://localhost:8080/tmf637/serviceQualification"
echo "    - GET  http://localhost:8080/tmf629/customer/{id}"
echo "    - POST http://localhost:8080/tmf622/productOrder"
echo "    - POST http://localhost:8080/tmf640/serviceActivation"
echo ""
echo "  Enhanced Catalog APIs:"
echo "    - GET/POST http://localhost:8080/api/service-specifications"
echo "    - GET/POST http://localhost:8080/api/product-offerings"
echo "    - GET      http://localhost:8080/api/geographic-locations"
echo "    - GET      http://localhost:8080/api/orders"
echo "    - POST     http://localhost:8080/api/sync"
echo ""
echo "Container logs: docker logs -f catalog-manager"
echo "Stop service:   docker stop catalog-manager"
echo "Remove service: docker rm catalog-manager"
echo ""

# 9. Create docker-compose.yml if it doesn't exist
if [ ! -f "docker-compose.yml" ]; then
    print_header "9. Creating docker-compose.yml"
    
    cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  catalog-manager:
    build: .
    image: catalog-manager:latest
    container_name: catalog-manager
    ports:
      - "8080:8080"
    environment:
      - FLASK_ENV=production
      - LOG_LEVEL=INFO
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 3s
      retries: 3
      start_period: 5s
    restart: unless-stopped
    volumes:
      - ./data:/app/data  # Optional: for data persistence
    networks:
      - telepath-network

networks:
  telepath-network:
    driver: bridge
EOF
    
    print_status 0 "Created docker-compose.yml"
    echo "   You can now use: docker-compose up -d"
fi

echo ""
echo "================================================"
echo -e "${GREEN}Setup Complete!${NC}"
echo "================================================"
echo ""

# Optional: Run diagnostics
read -p "Do you want to run full diagnostics? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if [ -f "catalog_diagnostics.py" ]; then
        echo "Running diagnostics..."
        python3 catalog_diagnostics.py http://localhost:8080
    else
        echo "Diagnostics script not found. Please run manually."
    fi
fi
