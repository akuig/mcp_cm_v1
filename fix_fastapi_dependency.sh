#!/bin/bash
# Fix FastAPI missing dependency

echo "🔧 Fixing FastAPI dependency for MCP server..."
echo "==========================================="
echo ""

# Step 1: Rebuild the MCP server image with updated requirements
echo "1️⃣ Rebuilding MCP server with FastAPI..."
docker-compose -f docker-compose-with-fault.yml build --no-cache mcp-server

if [ $? -ne 0 ]; then
    echo "❌ Build failed!"
    exit 1
fi

# Step 2: Restart the MCP server
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
    
    # Test the health endpoint
    echo ""
    echo "4️⃣ Testing health endpoint..."
    if curl -s http://localhost:8090/health | grep -q "http-streaming"; then
        echo "✅ HTTP streaming server is working!"
    else
        echo "⚠️  Health check didn't return expected response"
    fi
else
    echo "❌ MCP server failed to start"
    echo ""
    echo "Checking logs..."
    docker-compose -f docker-compose-with-fault.yml logs --tail=30 mcp-server
fi

echo ""
echo "✅ FastAPI dependency fix applied!"
echo ""
echo "Next steps:"
echo "1. Copy Claude config: cp claude_desktop_config_http.json ~/Library/Application\\ Support/Claude/claude_desktop_config.json"
echo "2. Restart Claude Desktop"
