#!/bin/bash

# Fix MCP Server add_tool AttributeError
echo "🔧 Fixing MCP Server add_tool AttributeError..."

# Stop the MCP server container
echo "⏹️  Stopping MCP server container..."
docker-compose stop mcp-server

# Remove the old container
echo "🗑️  Removing old container..."
docker-compose rm -f mcp-server

# Clear any cached images
echo "🧹 Clearing build cache..."
docker builder prune -f

# Rebuild the MCP server with fixed code
echo "🔨 Rebuilding MCP server (no cache)..."
docker-compose build --no-cache mcp-server

# Start the MCP server
echo "🚀 Starting MCP server..."
docker-compose up -d mcp-server

# Wait for startup
echo "⏰ Waiting for MCP server to be ready..."
sleep 15

# Check health
echo "🏥 Checking health..."
for i in {1..10}; do
    if curl -f http://localhost:8090/health &>/dev/null; then
        echo "✅ MCP server is healthy!"
        
        # Test tool discovery
        echo "🔍 Testing tool discovery..."
        tool_count=$(curl -s -X POST http://localhost:8090/mcp/stream \
            -H "Content-Type: application/json" \
            -d '{"jsonrpc":"2.0","id":"1","method":"tools/list","params":{}}' | jq '.result.tools | length' 2>/dev/null || echo "0")
        
        echo "📊 Found $tool_count tools available"
        
        if [ "$tool_count" -gt 0 ]; then
            echo "🎉 MCP server fixed and running with tools!"
            
            # List available tools
            echo "📋 Available tools:"
            curl -s -X POST http://localhost:8090/mcp/stream \
                -H "Content-Type: application/json" \
                -d '{"jsonrpc":"2.0","id":"1","method":"tools/list","params":{}}' | jq -r '.result.tools[]? | "  - \(.name): \(.description)"' 2>/dev/null || echo "  Could not list tools"
            
            exit 0
        else
            echo "⚠️  MCP server running but no tools found"
        fi
    else
        echo "⏳ Attempt $i/10: MCP server not ready yet..."
        sleep 3
    fi
done

echo "❌ MCP server health check failed after 10 attempts"
echo "📋 Checking logs..."
echo "==================== MCP SERVER LOGS ===================="
docker-compose logs --tail=30 mcp-server
echo "========================================================"

exit 1
