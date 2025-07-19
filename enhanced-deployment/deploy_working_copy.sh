#!/bin/bash
# Deploy EXACT COPY of working FastMCP approach with 1 tool

echo "🎯 Deploying EXACT COPY of working FastMCP approach..."
echo "📍 Working directory: $(pwd)"

# Stop the MCP server container
echo "🛑 Stopping MCP server container..."
docker compose stop mcp-server

# Remove the old container
echo "🗑️ Removing old container..."
docker compose rm -f mcp-server

# Rebuild and restart the MCP server
echo "🔨 Rebuilding with EXACT WORKING FASTMCP COPY..."
docker compose build mcp-server

echo "🚀 Starting exact copy of working FastMCP server..."
docker compose up -d mcp-server

# Wait a few seconds for startup
echo "⏳ Waiting for server startup..."
sleep 8

# Check that the server is running (FastMCP doesn't have /health endpoint)
echo "🏥 Checking if server is running..."
docker compose ps mcp-server

echo ""
echo "✅ EXACT WORKING FASTMCP COPY DEPLOYED!"
echo "🎯 This uses the EXACT same approach as the working 4-tool server"
echo "📋 Uses: from mcp.server.fastmcp import FastMCP"
echo "🔧 Uses: @mcp.tool() decorators"
echo "🌐 Uses: mcp.run(transport=\"streamable-http\")"
echo ""
echo "📊 Check logs with: docker compose logs mcp-server"
echo "🌐 Connect Claude to: http://localhost:8090/mcp/stream"
echo ""
echo "🕵️ Watch for: '🎉 CLAUDE USED TOOL!' in the logs"
echo "This should work since it's the exact same approach as the working version!"
