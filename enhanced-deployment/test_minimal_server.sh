#!/bin/bash
# Test minimal MCP server for Claude debugging

echo "🧪 Testing MINIMAL MCP Server for Claude debugging..."
echo "📍 Working directory: $(pwd)"

# Stop the MCP server container
echo "🛑 Stopping MCP server container..."
docker compose stop mcp-server

# Remove the old container
echo "🗑️ Removing old container..."
docker compose rm -f mcp-server

# Rebuild and restart the MCP server
echo "🔨 Rebuilding MCP server with MINIMAL test version..."
docker compose build mcp-server

echo "🚀 Starting minimal test MCP server..."
docker compose up -d mcp-server

# Wait a few seconds for startup
echo "⏳ Waiting for server startup..."
sleep 5

# Check health
echo "🏥 Checking server health..."
curl -f http://localhost:8090/health | jq '.'

echo ""
echo "🧪 MINIMAL TEST VERSION DEPLOYED!"
echo "🎯 This version has only 1 tool: service_qualification"
echo "🔍 Should help us isolate if the issue is with tool complexity"
echo ""
echo "📊 Check logs with: docker compose logs mcp-server"
echo "🌐 Connect Claude to: http://localhost:8090/mcp/stream"
echo ""
echo "🕵️ Watch for this log message: '📋 🎉 CLAUDE REQUESTED TOOLS LIST! 🎉'"
echo "If you see this, the protocol fix works and the issue was tool complexity!"
