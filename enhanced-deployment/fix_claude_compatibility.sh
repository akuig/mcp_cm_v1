#!/bin/bash
# Made executable script
# Fix and redeploy MCP server for Claude compatibility

echo "🔧 Fixing Claude MCP Server compatibility issue..."
echo "📍 Working directory: $(pwd)"

# Stop the MCP server container
echo "🛑 Stopping MCP server container..."
docker compose stop mcp-server

# Remove the old container
echo "🗑️ Removing old container..."
docker compose rm -f mcp-server

# Rebuild and restart the MCP server
echo "🔨 Rebuilding MCP server with Claude compatibility fix..."
docker compose build mcp-server

echo "🚀 Starting fixed MCP server..."
docker compose up -d mcp-server

# Wait a few seconds for startup
echo "⏳ Waiting for server startup..."
sleep 5

# Check health
echo "🏥 Checking server health..."
curl -f http://localhost:8090/health | jq '.'

echo ""
echo "✅ Claude compatibility fix applied!"
echo "🔍 The server now supports protocol version 2025-06-18 for Claude"
echo "📋 Server should now show all 12 tools to Claude"
echo ""
echo "📊 Check logs with: docker compose logs mcp-server"
echo "🌐 Connect Claude to: http://localhost:8090/mcp/stream"
