#!/bin/bash
# Fix and restart the MCP server

echo "🔧 Fixing MCP server configuration..."

# Step 1: Stop all containers
echo "📦 Stopping all containers..."
docker-compose -f docker-compose-with-fault.yml down

# Step 2: Rebuild the MCP server image
echo "🏗️  Rebuilding MCP server image..."
docker-compose -f docker-compose-with-fault.yml build mcp-server

# Step 3: Start all services
echo "🚀 Starting all services..."
docker-compose -f docker-compose-with-fault.yml up -d

# Step 4: Wait for services
echo "⏳ Waiting for services to initialize (20 seconds)..."
sleep 20

# Step 5: Check status
echo "🔍 Checking service status..."
docker-compose -f docker-compose-with-fault.yml ps

echo ""
echo "📋 MCP Server logs:"
docker-compose -f docker-compose-with-fault.yml logs --tail=20 mcp-server

echo ""
echo "✅ Done! Check if all services are running above."
echo ""
echo "To run the demo: python test_fault_management.py"
