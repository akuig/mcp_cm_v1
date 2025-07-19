#!/bin/bash
# Test FastMCP server - use original library approach

echo "🧪 Testing FASTMCP MCP Server approach..."
echo "📍 Working directory: $(pwd)"

# Stop the MCP server container
echo "🛑 Stopping MCP server container..."
docker compose stop mcp-server

# Remove the old container
echo "🗑️ Removing old container..."
docker compose rm -f mcp-server

# Rebuild and restart the MCP server
echo "🔨 Rebuilding MCP server with FastMCP library approach..."
docker compose build mcp-server

echo "🚀 Starting FastMCP test server..."
docker compose up -d mcp-server

# Wait a few seconds for startup
echo "⏳ Waiting for server startup..."
sleep 5

# Check health
echo "🏥 Checking server health..."
curl -f http://localhost:8090/health 2>/dev/null || echo "Health endpoint not available (FastMCP doesn't expose /health)"

echo ""
echo "🧪 FASTMCP TEST VERSION DEPLOYED!"
echo "🎯 This version uses the original FastMCP library like the working version"
echo "🔧 Uses mcp.server.fastmcp.FastMCP instead of custom HTTP implementation"
echo ""
echo "📊 Check logs with: docker compose logs mcp-server"
echo "🌐 Connect Claude to: http://localhost:8090/mcp/stream"
echo ""
echo "🕵️ Look for: '📋 🎉 CLAUDE USED A TOOL! 🎉' in the logs"
echo "If Claude uses the tool, this approach works!"
