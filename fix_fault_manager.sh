#!/bin/bash
# Fix fault manager health check issue

echo "🔧 Fixing Fault Manager Health Check..."
echo "======================================="
echo ""

# Step 1: Stop all services
echo "📦 Stopping services..."
docker-compose -f docker-compose-with-fault.yml down

# Step 2: Rebuild fault manager with curl installed
echo "🏗️  Rebuilding fault manager..."
docker-compose -f docker-compose-with-fault.yml build fault-manager

# Step 3: Start just the essential services first
echo "🚀 Starting core services..."
docker-compose -f docker-compose-with-fault.yml up -d postgres
sleep 5

docker-compose -f docker-compose-with-fault.yml up -d catalog-manager
sleep 10

docker-compose -f docker-compose-with-fault.yml up -d fault-manager
echo "⏳ Waiting for fault manager to start (30 seconds)..."
sleep 30

# Step 4: Check fault manager health
echo "🔍 Checking fault manager health..."
curl -s http://localhost:8081/health && echo -e "\n✅ Fault manager is healthy!" || echo -e "\n❌ Fault manager not responding"

# Step 5: Start MCP server
echo -e "\n🚀 Starting MCP server..."
docker-compose -f docker-compose-with-fault.yml up -d mcp-server

# Step 6: Final status check
sleep 10
echo -e "\n📊 Final service status:"
docker-compose -f docker-compose-with-fault.yml ps

echo -e "\n✅ Done! Check the status above."
echo ""
echo "To see logs: docker-compose -f docker-compose-with-fault.yml logs fault-manager"
echo "To test: curl http://localhost:8081/health"
