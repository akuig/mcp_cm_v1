#!/bin/bash

# Quick setup script for Telepath AI Enhanced Catalog Manager
# This script makes all necessary files executable and provides deployment guidance

echo "🚀 Telepath AI Enhanced Catalog Manager - Setup Script"
echo "======================================================="

# Make scripts executable
chmod +x deploy.sh
chmod +x validate_apis.py

echo "✅ Made deployment scripts executable"

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Please install Docker Desktop first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose not found. Please install Docker Compose first."
    exit 1
fi

echo "✅ Docker and Docker Compose are available"

# Check available ports
echo "🔍 Checking port availability..."
ports_to_check=(3000 3306 6379 8080 8081 8082 9090)
unavailable_ports=()

for port in "${ports_to_check[@]}"; do
    if lsof -i :$port &> /dev/null; then
        unavailable_ports+=($port)
    fi
done

if [ ${#unavailable_ports[@]} -gt 0 ]; then
    echo "⚠️  Warning: These ports are in use: ${unavailable_ports[*]}"
    echo "   You may need to stop other services or the deployment may fail."
else
    echo "✅ All required ports are available"
fi

echo ""
echo "📋 DEPLOYMENT SUMMARY"
echo "===================="
echo "Enhanced MCP Server: 12 total tools (4 existing + 8 new)"
echo "TMF Forum APIs: TMF620, TMF629, TMF633, TMF637, TMF640, TMF673"  
echo "Sample Data: 9 services, 14 products, 13 locations, 8 customers"
echo "Geographic Coverage: Springfield, Shelbyville, Capital City, Ogdenville"
echo "Test Customer: 8452934 (Jane Doe) - Active account in Springfield"
echo ""
echo "🎯 QUICK START"
echo "=============="
echo "1. Deploy the system:"
echo "   ./deploy.sh deploy"
echo ""
echo "2. Validate everything works:"
echo "   python validate_apis.py"
echo ""
echo "3. Access the system:"
echo "   • Web UI: http://localhost:8082"
echo "   • API Health: http://localhost:8080/admin/health"
echo "   • Grafana: http://localhost:3000 (admin/admin)"
echo ""
echo "4. Test key functionality:"
echo "   • Service qualification for customer 8452934"
echo "   • Customer lookup returns Jane Doe"
echo "   • Geographic coverage shows Springfield services"
echo "   • All 12 MCP tools available"
echo ""
echo "📚 AVAILABLE COMMANDS"
echo "===================="
echo "./deploy.sh deploy     - Full deployment"
echo "./deploy.sh start      - Start services"
echo "./deploy.sh stop       - Stop services"
echo "./deploy.sh status     - Check status"
echo "./deploy.sh logs       - View logs"
echo "./deploy.sh test       - Test APIs"
echo "python validate_apis.py - Comprehensive validation"
echo ""
echo "🎉 Ready to deploy! Run './deploy.sh deploy' to start."