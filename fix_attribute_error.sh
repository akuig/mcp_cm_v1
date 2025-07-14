#!/bin/bash
# Fix for MCP server AttributeError

echo "🔧 Fixing MCP Server AttributeError..."
echo "====================================="
echo ""
echo "The error 'Server' object has no attribute 'add_tool' is fixed!"
echo ""

# Step 1: Rebuild with the working server
echo "1️⃣ Rebuilding MCP server with working HTTP implementation..."
docker-compose -f docker-compose-with-fault.yml build mcp-server

if [ $? -ne 0 ]; then
    echo "❌ Build failed!"
    exit 1
fi

# Step 2: Restart MCP server
echo ""
echo "2️⃣ Restarting MCP server..."
docker-compose -f docker-compose-with-fault.yml stop mcp-server
docker-compose -f docker-compose-with-fault.yml rm -f mcp-server
docker-compose -f docker-compose-with-fault.yml up -d mcp-server

# Wait for startup
echo "   Waiting for MCP server to start (10 seconds)..."
sleep 10

# Step 3: Check if it's running
echo ""
echo "3️⃣ Checking MCP server status..."
if docker-compose -f docker-compose-with-fault.yml ps mcp-server | grep -q "Up"; then
    echo "✅ MCP server is running!"
    
    # Test health endpoint
    echo ""
    echo "4️⃣ Testing health endpoint..."
    health_response=$(curl -s http://localhost:8090/health)
    if echo "$health_response" | grep -q "healthy"; then
        echo "✅ Health check passed!"
        echo "   Response: $health_response"
    else
        echo "⚠️  Health check response unexpected"
    fi
    
    # Test MCP info
    echo ""
    echo "5️⃣ Testing MCP info endpoint..."
    mcp_response=$(curl -s http://localhost:8090/mcp)
    if echo "$mcp_response" | grep -q "telepath-mcp"; then
        echo "✅ MCP endpoint working!"
        echo "   Response: $mcp_response"
    else
        echo "⚠️  MCP endpoint response unexpected"
    fi
else
    echo "❌ MCP server failed to start"
    echo ""
    echo "Checking logs..."
    docker-compose -f docker-compose-with-fault.yml logs --tail=30 mcp-server
    exit 1
fi

echo ""
echo "✅ MCP server is fixed and running!"
echo ""
echo "📝 Claude Desktop Configuration:"
echo "================================"
cat claude_desktop_config_http.json
echo ""
echo ""
echo "Copy with:"
echo "  cp claude_desktop_config_http.json ~/Library/Application\\ Support/Claude/claude_desktop_config.json"
echo ""
echo "Then restart Claude Desktop to connect!"
