#!/bin/bash
# Setup script for Telepath AI Demo with Fault Management

echo "Setting up Telepath AI Demo with Fault Management..."

# Stop any existing containers
echo "Stopping existing containers..."
docker-compose -f docker-compose-with-fault.yml down

# Build all services
echo "Building Docker images..."
docker-compose -f docker-compose-with-fault.yml build

# Start services
echo "Starting services..."
docker-compose -f docker-compose-with-fault.yml up -d

# Wait for services to be ready
echo "Waiting for services to be ready..."
sleep 15

# Check service health
echo ""
echo "Checking service status..."
echo -n "PostgreSQL: "
docker-compose -f docker-compose-with-fault.yml exec postgres pg_isready -U telecom_user && echo "✓ Ready" || echo "✗ Not ready"

echo -n "Catalog Manager: "
curl -s http://localhost:8080/health > /dev/null 2>&1 && echo "✓ Ready" || echo "✗ Not ready"

echo -n "Fault Manager: "
curl -s http://localhost:8081/docs > /dev/null 2>&1 && echo "✓ Ready" || echo "✗ Not ready"

echo -n "MCP Server: "
curl -s http://localhost:8090/health > /dev/null 2>&1 && echo "✓ Ready" || echo "✗ Not ready"

echo ""
echo "Setup complete! The fault management demo is ready."
echo ""
echo "Available endpoints:"
echo "- Catalog Manager: http://localhost:8080"
echo "- Fault Manager API: http://localhost:8081/docs"
echo "- MCP Server: http://localhost:8090"
echo ""
echo "To run the fault management demo:"
echo "  python test_fault_management.py"
echo ""
echo "To view logs:"
echo "  docker-compose -f docker-compose-with-fault.yml logs -f"
echo ""
echo "To stop all services:"
echo "  docker-compose -f docker-compose-with-fault.yml down"
