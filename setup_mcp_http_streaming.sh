#!/bin/bash
# Setup MCP HTTP Streaming for Claude Desktop

echo "🚀 Setting up MCP HTTP Streaming for Claude Desktop"
echo "=================================================="
echo ""

# Step 1: Stop and rebuild MCP server
echo "1️⃣ Rebuilding MCP server with HTTP streaming..."
docker-compose -f docker-compose-with-fault.yml stop mcp-server
docker-compose -f docker-compose-with-fault.yml build mcp-server

# Step 2: Start all services
echo ""
echo "2️⃣ Starting all services..."
docker-compose -f docker-compose-with-fault.yml up -d

# Wait for services
echo "   Waiting for services to start (20 seconds)..."
sleep 20

# Step 3: Test the MCP server
echo ""
echo "3️⃣ Testing MCP HTTP streaming endpoint..."
if curl -s http://localhost:8090/health | grep -q "http-streaming"; then
    echo "   ✅ MCP server is running with HTTP streaming!"
else
    echo "   ❌ MCP server health check failed"
    echo "   Checking logs..."
    docker-compose -f docker-compose-with-fault.yml logs --tail=20 mcp-server
    exit 1
fi

# Test MCP endpoints
echo ""
echo "4️⃣ Testing MCP endpoints..."
echo "   Checking /mcp/stream endpoint..."
curl -s -X POST http://localhost:8090/mcp/stream \
  -H "Content-Type: application/json" \
  -d '{"method": "ping"}' \
  --max-time 2 || echo "   Note: Endpoint requires proper MCP client"

# Step 4: Configure Claude Desktop
echo ""
echo "5️⃣ Claude Desktop Configuration"
echo "================================"
echo ""
echo "Copy this configuration to Claude Desktop:"
echo "(Usually at ~/Library/Application Support/Claude/claude_desktop_config.json)"
echo ""
cat claude_desktop_config_http.json
echo ""
echo ""
echo "Or copy with:"
echo "cp claude_desktop_config_http.json ~/Library/Application\\ Support/Claude/claude_desktop_config.json"

# Step 5: Verify services
echo ""
echo "6️⃣ Service Status:"
docker-compose -f docker-compose-with-fault.yml ps

echo ""
echo "✅ Setup Complete!"
echo ""
echo "📝 Next Steps:"
echo "1. Copy the configuration above to Claude Desktop"
echo "2. Restart Claude Desktop"
echo "3. Connect to 'telepath-fault-http' in Claude"
echo ""
echo "🔍 MCP Endpoints:"
echo "   Base URL: http://localhost:8090"
echo "   Health: http://localhost:8090/health"
echo "   Stream: http://localhost:8090/mcp/stream"
echo "   SSE: http://localhost:8090/mcp/sse"
echo ""
echo "📊 Available Tools:"
echo "   • service_qualification"
echo "   • customer_management"
echo "   • product_ordering"
echo "   • service_activation"
echo "   • check_service_status (Fault detection)"
echo "   • create_trouble_ticket"
echo "   • execute_remedial_action"
echo "   • get_service_problems"
