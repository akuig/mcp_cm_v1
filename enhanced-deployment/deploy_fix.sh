#!/bin/bash

echo "🔧 Deploying Fixed MCP Server..."

# Navigate to the enhanced-deployment directory
cd /Users/joe/dev/mcp_cm_v1/enhanced-deployment

# Replace the broken server with the fixed one
echo "📋 Replacing broken server with fixed version..."
cp mcp-server/mcp_server_fixed.py mcp-server/mcp_server_working.py

echo "✅ Fixed MCP server code deployed"

# Rebuild and restart the MCP container
echo "🔄 Rebuilding MCP container..."
docker-compose down mcp-server
docker-compose build mcp-server --no-cache
docker-compose up -d mcp-server

# Wait a moment for startup
echo "⏳ Waiting for server to start..."
sleep 10

# Check if the server is running
echo "🔍 Checking server status..."
docker-compose logs mcp-server --tail 20

echo ""
echo "🩺 Testing health endpoint..."
curl -s http://localhost:8090/health | jq . || echo "Health check failed"

echo ""
echo "✅ Fixed MCP Server deployment complete!"
echo ""
echo "🎯 The bug was in the tools/list handler - it was trying to call a"
echo "   decorator function incorrectly, which caused Claude Desktop to"
echo "   connect but not see any tools."
echo ""
echo "🔧 Next steps:"
echo "1. In Claude Desktop, go to 'Manage Connectors'"
echo "2. Remove the old Telepath connector if it exists"
echo "3. Add a new custom connector:"
echo "   - Name: Telepath Enhanced Fixed"
echo "   - URL: http://localhost:8090/mcp/stream"
echo "   - Method: HTTP"
echo "4. Claude should now see all 12 tools!"
echo ""
echo "🎉 You should now see these 12 tools in Claude:"
echo "   1. service_qualification"
echo "   2. customer_management"
echo "   3. product_ordering"
echo "   4. service_activation"
echo "   5. list_service_specifications"
echo "   6. list_product_offerings"
echo "   7. list_geographic_locations"
echo "   8. sync_catalog_data"
echo "   9. create_service_specification"
echo "   10. create_product_offering"
echo "   11. link_offering_to_specification"
echo "   12. add_geographic_coverage"
