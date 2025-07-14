#!/bin/bash
# Fix for MCP server asyncio error

echo "🔧 Fixing MCP Server AsyncIO Error..."
echo "===================================="
echo ""

# Step 1: Just rebuild MCP server
echo "🏗️  Rebuilding MCP server..."
docker-compose -f docker-compose-with-fault.yml build mcp-server

# Step 2: Restart MCP server
echo "🔄 Restarting MCP server..."
docker-compose -f docker-compose-with-fault.yml stop mcp-server
docker-compose -f docker-compose-with-fault.yml rm -f mcp-server
docker-compose -f docker-compose-with-fault.yml up -d mcp-server

# Wait a bit
sleep 5

# Step 3: Check status
echo ""
echo "📊 Checking MCP server status..."
docker-compose -f docker-compose-with-fault.yml ps mcp-server

echo ""
echo "📋 MCP server logs (last 20 lines):"
docker-compose -f docker-compose-with-fault.yml logs --tail=20 mcp-server

echo ""
echo "✅ Fix applied! The MCP server should now start correctly."
echo ""
echo "To run the demo: python test_fault_management.py"
