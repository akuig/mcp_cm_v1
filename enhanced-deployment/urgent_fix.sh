#!/bin/bash
# URGENT FIX - Revert from broken FastMCP and try MCP spec compliant version

echo "🚨 URGENT FIX: Reverting from broken FastMCP approach..."
echo "📍 Working directory: $(pwd)"

# Stop the MCP server container
echo "🛑 Stopping broken MCP server container..."
docker compose stop mcp-server

# Remove the old container
echo "🗑️ Removing broken container..."
docker compose rm -f mcp-server

# Rebuild and restart the MCP server
echo "🔨 Rebuilding with MCP SPEC COMPLIANT version..."
docker compose build mcp-server

echo "🚀 Starting MCP spec compliant server..."
docker compose up -d mcp-server

# Wait a few seconds for startup
echo "⏳ Waiting for server startup..."
sleep 5

# Check health
echo "🏥 Checking server health..."
curl -f http://localhost:8090/health | jq '.'

echo ""
echo "✅ MCP SPEC COMPLIANT VERSION DEPLOYED!"
echo "🔧 This version includes complete capabilities structure"
echo "🎯 Added: resources, prompts, logging, completion capabilities"
echo "📋 Should fix the issue that prevented Claude from requesting tools"
echo ""
echo "📊 Check logs with: docker compose logs mcp-server"
echo "🌐 Connect Claude to: http://localhost:8090/mcp/stream"
echo ""
echo "🕵️ Watch for: '📋 🎉 SUCCESS! CLAUDE REQUESTED TOOLS LIST! 🎉'"
