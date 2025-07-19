#!/bin/bash

# Fix MCP Server Import Issues
echo "🔧 Fixing MCP Server Import Issues..."

# Stop the MCP server container
echo "⏹️  Stopping MCP server container..."
docker-compose stop mcp-server

# Remove the old container
echo "🗑️  Removing old container..."
docker-compose rm -f mcp-server

# Rebuild the MCP server with fixed code
echo "🔨 Rebuilding MCP server..."
docker-compose build --no-cache mcp-server

# Start the MCP server
echo "🚀 Starting MCP server..."
docker-compose up -d mcp-server

# Wait for startup
echo "⏰ Waiting for MCP server to be ready..."
sleep 10

# Check health
echo "🏥 Checking health..."
if curl -f http://localhost:8090/health &>/dev/null; then
    echo "✅ MCP server is healthy!"
    
    # Test tool discovery
    echo "🔍 Testing tool discovery..."
    curl -s -X POST http://localhost:8090/mcp/stream \
        -H "Content-Type: application/json" \
        -d '{"jsonrpc":"2.0","id":"1","method":"tools/list","params":{}}' | jq '.result.tools | length'
    
    echo "🎉 MCP server fixed and running!"
else
    echo "❌ MCP server health check failed"
    echo "📋 Checking logs..."
    docker-compose logs --tail=20 mcp-server
fi
