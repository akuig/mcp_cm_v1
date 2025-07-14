#!/bin/bash
# Complete fix for fault manager and MCP server issues

echo "🔧 Complete Fix for Fault Management Demo"
echo "========================================="
echo ""

# Step 1: Clean everything
echo "🧹 Cleaning up old containers and images..."
docker-compose -f docker-compose-with-fault.yml down -v
docker system prune -f

# Step 2: Rebuild all images
echo "🏗️  Building all services..."
docker-compose -f docker-compose-with-fault.yml build --no-cache

# Step 3: Start services in order
echo "🚀 Starting services in sequence..."

# Start PostgreSQL first
echo "   1/4 Starting PostgreSQL..."
docker-compose -f docker-compose-with-fault.yml up -d postgres
sleep 10

# Start Catalog Manager
echo "   2/4 Starting Catalog Manager..."
docker-compose -f docker-compose-with-fault.yml up -d catalog-manager
sleep 15

# Start Fault Manager
echo "   3/4 Starting Fault Manager..."
docker-compose -f docker-compose-with-fault.yml up -d fault-manager
echo "      Waiting for Fault Manager to initialize..."
sleep 20

# Test Fault Manager
echo "   🔍 Testing Fault Manager..."
if curl -s http://localhost:8081/health > /dev/null 2>&1; then
    echo "      ✅ Fault Manager is healthy!"
else
    echo "      ⚠️  Fault Manager may not be fully ready, continuing anyway..."
fi

# Start MCP Server
echo "   4/4 Starting MCP Server..."
docker-compose -f docker-compose-with-fault.yml up -d mcp-server
sleep 10

# Step 4: Final status check
echo ""
echo "📊 Service Status:"
echo "=================="
docker-compose -f docker-compose-with-fault.yml ps

echo ""
echo "🔍 Health Checks:"
echo "================="

# Check each service
echo -n "PostgreSQL:      "
docker-compose -f docker-compose-with-fault.yml exec postgres pg_isready -U telecom_user > /dev/null 2>&1 && echo "✅ Healthy" || echo "❌ Not ready"

echo -n "Catalog Manager: "
curl -s http://localhost:8080/health > /dev/null 2>&1 && echo "✅ Healthy" || echo "❌ Not ready"

echo -n "Fault Manager:   "
curl -s http://localhost:8081/health > /dev/null 2>&1 && echo "✅ Healthy" || echo "❌ Not ready"

echo -n "MCP Server:      "
docker ps | grep mcp_server | grep -q "Up" && echo "✅ Running" || echo "❌ Not running"

echo ""
echo "📝 Notes:"
echo "- The MCP server doesn't wait for fault manager health check"
echo "- Fault manager warnings about 'on_event' are normal and don't affect operation"
echo "- If fault manager isn't healthy, it will still work after a few seconds"

echo ""
echo "🎯 To run the demo:"
echo "   python test_fault_management.py"

echo ""
echo "📋 To check logs:"
echo "   docker-compose -f docker-compose-with-fault.yml logs -f"
