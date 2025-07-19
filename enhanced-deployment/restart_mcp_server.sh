#!/bin/bash

# Make sure we're in the right directory
cd "$(dirname "$0")"

echo "🔄 Restarting MCP Server with debugging..."

# Stop the current container
echo "⏹️  Stopping current MCP server..."
docker-compose stop mcp-server

# Rebuild the MCP server image
echo "🔨 Rebuilding MCP server image..."
docker-compose build mcp-server

# Start the MCP server
echo "🚀 Starting MCP server..."
docker-compose up -d mcp-server

# Wait a bit for startup
echo "⏳ Waiting for server to start..."
sleep 5

# Check status
echo "📊 Checking container status..."
docker-compose ps mcp-server

# Show recent logs
echo "📋 Recent logs:"
docker-compose logs --tail=20 mcp-server

echo "✅ MCP Server restart complete!"
echo "🔍 To monitor logs: docker-compose logs -f mcp-server"
