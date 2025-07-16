#!/bin/bash

echo "🔧 Fixing MCP Server import issues..."

# Stop the failing MCP server
docker-compose stop mcp-server

# Remove the old image to force rebuild
docker rmi enhanced-deployment-mcp-server:latest 2>/dev/null || true

echo "✅ Stopped MCP server and removed old image"

# Rebuild and restart the MCP server
echo "🚀 Rebuilding MCP server with fixed imports..."
docker-compose up -d --build mcp-server

echo "⏳ Waiting for MCP server to start..."
sleep 10

# Check if it's running properly
if docker-compose ps mcp-server | grep -q "Up"; then
    echo "✅ MCP Server is now running!"
    echo "📋 Checking logs..."
    docker-compose logs --tail=20 mcp-server
else
    echo "❌ MCP Server still having issues. Checking logs..."
    docker-compose logs --tail=30 mcp-server
fi

echo ""
echo "🎯 Current service status:"
docker-compose ps