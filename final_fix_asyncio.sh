#!/bin/bash
# Final fix for all issues - AsyncIO error fixed

echo "🔧 Complete Fix for MCP Server AsyncIO Error"
echo "==========================================="
echo ""

# Step 1: Stop everything
echo "📦 Stopping all services..."
docker-compose -f docker-compose-with-fault.yml down

# Step 2: Rebuild MCP server with fixed code
echo "🏗️  Rebuilding MCP server with AsyncIO fix..."
docker-compose -f docker-compose-with-fault.yml build mcp-server

# Step 3: Start services in order
echo "🚀 Starting services..."
docker-compose -f docker-compose-with-fault.yml up -d postgres
sleep 5

docker-compose -f docker-compose-with-fault.yml up -d catalog-manager
sleep 10

docker-compose -f docker-compose-with-fault.yml up -d fault-manager
sleep 10

docker-compose -f docker-compose-with-fault.yml up -d mcp-server
sleep 5

# Step 4: Check status
echo ""
echo "📊 Service Status:"
docker-compose -f docker-compose-with-fault.yml ps

echo ""
echo "🔍 Checking MCP Server..."
if docker-compose -f docker-compose-with-fault.yml ps mcp-server | grep -q "Up"; then
    echo "✅ MCP Server is running!"
else
    echo "❌ MCP Server failed to start. Checking logs..."
    docker-compose -f docker-compose-with-fault.yml logs --tail=20 mcp-server
fi

echo ""
echo "✅ AsyncIO fix applied!"
echo ""
echo "To run the demo: python test_fault_management.py"
echo ""
echo "If issues persist, try the simple version:"
echo "  docker-compose -f docker-compose-with-fault.yml run --rm mcp-server python mcp_fastmcp_server_fault_simple.py"
