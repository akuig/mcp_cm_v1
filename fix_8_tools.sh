#!/bin/bash
# Fix MCP server to show all 8 tools

echo "🔧 Fixing MCP Server to Show All 8 Tools"
echo "========================================"
echo ""
echo "The server is running but only showing 4 tools. Let's fix this!"
echo ""

# Step 1: Rebuild with the new server that has all 8 tools
echo "1️⃣ Rebuilding MCP server with all 8 tools..."
docker-compose -f docker-compose-with-fault.yml build mcp-server

if [ $? -ne 0 ]; then
    echo "❌ Build failed!"
    exit 1
fi

# Step 2: Stop and restart the MCP server
echo ""
echo "2️⃣ Restarting MCP server..."
docker-compose -f docker-compose-with-fault.yml stop mcp-server
docker-compose -f docker-compose-with-fault.yml rm -f mcp-server
docker-compose -f docker-compose-with-fault.yml up -d mcp-server

# Wait for it to start
echo "   Waiting for MCP server to start..."
sleep 10

# Step 3: Check if it's running
echo ""
echo "3️⃣ Checking MCP server status..."
if docker-compose -f docker-compose-with-fault.yml ps mcp-server | grep -q "Up"; then
    echo "✅ MCP server is running!"
    
    # Check logs to confirm all tools
    echo ""
    echo "4️⃣ Verifying tools are loaded..."
    docker-compose -f docker-compose-with-fault.yml logs --tail=20 mcp-server | grep -q "Available tools: 8" && echo "✅ All 8 tools confirmed!" || echo "⚠️  Check logs for tool count"
else
    echo "❌ MCP server failed to start"
    echo ""
    echo "Checking logs..."
    docker-compose -f docker-compose-with-fault.yml logs --tail=30 mcp-server
    exit 1
fi

echo ""
echo "✅ MCP server fixed with all 8 tools!"
echo ""
echo "📝 Now in Claude Desktop:"
echo "1. Disconnect and reconnect to 'telepath-fault-http'"
echo "2. You should see 8 tools:"
echo "   - service_qualification"
echo "   - customer_management"
echo "   - product_ordering"
echo "   - service_activation"
echo "   - check_service_status (NEW)"
echo "   - create_trouble_ticket (NEW)"
echo "   - execute_remedial_action (NEW)"
echo "   - get_service_problems (NEW)"
echo ""
echo "Try: 'Check for service issues at 123 Main Street Dublin'"
