#!/bin/bash
# Setup MCP server for Claude Desktop with Fault Management

echo "🤖 Setting up MCP Server for Claude Desktop"
echo "=========================================="
echo ""

# Step 1: Make sure services are running locally
echo "1️⃣ Checking if local services are running..."

# Check Catalog Manager
if curl -s http://localhost:8080/health > /dev/null 2>&1; then
    echo "   ✅ Catalog Manager is running on localhost:8080"
else
    echo "   ❌ Catalog Manager not running!"
    echo "   Start it with: docker-compose -f docker-compose-with-fault.yml up -d catalog-manager"
    exit 1
fi

# Check Fault Manager
if curl -s http://localhost:8081/health > /dev/null 2>&1; then
    echo "   ✅ Fault Manager is running on localhost:8081"
else
    echo "   ❌ Fault Manager not running!"
    echo "   Start it with: docker-compose -f docker-compose-with-fault.yml up -d fault-manager"
    exit 1
fi

# Step 2: Build the Docker image with STDIO support
echo ""
echo "2️⃣ Building MCP Docker image with STDIO support..."
docker build -t telepath-mcp:latest -f Dockerfile.mcp .

# Step 3: Test the MCP server
echo ""
echo "3️⃣ Testing MCP server (STDIO mode)..."
echo '{"jsonrpc": "2.0", "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}}, "id": 1}' | \
docker run --rm -i --network host \
    -e CATALOG_MANAGER_URL=http://localhost:8080 \
    -e FAULT_MANAGER_URL=http://localhost:8081 \
    telepath-mcp:latest python /app/mcp_stdio_server_fault.py 2>/dev/null | head -5

if [ $? -eq 0 ]; then
    echo ""
    echo "   ✅ MCP server is working in STDIO mode!"
else
    echo ""
    echo "   ❌ MCP server test failed"
    exit 1
fi

# Step 4: Provide Claude Desktop configuration
echo ""
echo "4️⃣ Claude Desktop Configuration"
echo "================================"
echo ""
echo "Add this to your Claude Desktop configuration:"
echo "(Usually at ~/Library/Application Support/Claude/claude_desktop_config.json on macOS)"
echo ""
cat claude_desktop_config_fault.json
echo ""
echo ""
echo "Or copy it directly with:"
echo "cp claude_desktop_config_fault.json ~/Library/Application\\ Support/Claude/claude_desktop_config.json"
echo ""

# Step 5: Instructions
echo "📝 Final Steps:"
echo "=============="
echo "1. Copy the configuration above to Claude Desktop config file"
echo "2. Restart Claude Desktop"
echo "3. The MCP tools should appear in Claude's interface"
echo ""
echo "⚠️  Important: Services must be running locally (not through ngrok)"
echo "   - Catalog Manager: http://localhost:8080"
echo "   - Fault Manager: http://localhost:8081"
echo ""
echo "🎯 Available Tools in Claude:"
echo "   • service_qualification - Check service availability"
echo "   • customer_management - Get customer info"
echo "   • product_ordering - Create orders"
echo "   • service_activation - Activate services"
echo "   • check_service_status - Check for network faults"
echo "   • create_trouble_ticket - Create trouble tickets"
echo "   • execute_remedial_action - Execute fixes"
echo "   • get_service_problems - List area problems"
echo ""
echo "✅ Setup complete!"
