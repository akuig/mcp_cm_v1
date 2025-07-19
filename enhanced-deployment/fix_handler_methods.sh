#!/bin/bash

# Fix MCP Server Handler Methods Issue
echo "🔧 Fixing MCP Server Handler Methods Issue..."
echo "   - Removed dependency on MCP Server handler registration"
echo "   - Using pure HTTP JSON-RPC implementation"

# Stop the MCP server container
echo "⏹️  Stopping MCP server container..."
docker-compose stop mcp-server

# Remove the old container
echo "🗑️  Removing old container..."
docker-compose rm -f mcp-server

# Clear any cached images
echo "🧹 Clearing build cache..."
docker builder prune -f

# Rebuild the MCP server with pure HTTP implementation
echo "🔨 Rebuilding MCP server (pure HTTP implementation)..."
docker-compose build --no-cache mcp-server

# Start the MCP server
echo "🚀 Starting MCP server..."
docker-compose up -d mcp-server

# Wait for startup and test
echo "⏰ Waiting for MCP server to be ready..."
for i in {1..15}; do
    sleep 2
    echo "   Attempt $i/15: Testing health endpoint..."
    
    if curl -f http://localhost:8090/health &>/dev/null; then
        echo "✅ MCP server is healthy!"
        
        # Get health info
        echo "🏥 Health status:"
        curl -s http://localhost:8090/health | jq '.' 2>/dev/null || echo "   Could not parse health response"
        
        # Test MCP info endpoint
        echo "📊 MCP info:"
        curl -s http://localhost:8090/mcp | jq '.tools_count' 2>/dev/null || echo "   Could not get tool count"
        
        # Test tool discovery
        echo "🔍 Testing tool discovery..."
        tool_response=$(curl -s -X POST http://localhost:8090/mcp/stream \
            -H "Content-Type: application/json" \
            -d '{"jsonrpc":"2.0","id":"1","method":"tools/list","params":{}}')
        
        if echo "$tool_response" | jq '.result.tools | length' &>/dev/null; then
            tool_count=$(echo "$tool_response" | jq '.result.tools | length')
            echo "📋 Found $tool_count tools available!"
            
            if [ "$tool_count" -gt 0 ]; then
                echo "🎉 MCP server successfully fixed and running!"
                echo ""
                echo "📋 Available tools:"
                echo "$tool_response" | jq -r '.result.tools[]? | "  - \(.name): \(.description)"' 2>/dev/null
                
                echo ""
                echo "✅ SUCCESS: Pure HTTP MCP server is working!"
                echo "🔗 Claude Desktop should now be able to connect and see all $tool_count tools"
                exit 0
            fi
        fi
        
        echo "⚠️  MCP server running but tool discovery failed"
        echo "📋 Raw response: $tool_response"
    else
        echo "   ⏳ Not ready yet..."
    fi
done

echo "❌ MCP server failed to start properly"
echo "📋 Checking logs..."
echo "==================== MCP SERVER LOGS ===================="
docker-compose logs --tail=20 mcp-server
echo "========================================================"

exit 1
