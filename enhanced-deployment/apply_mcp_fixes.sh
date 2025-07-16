#!/bin/bash

echo "🔧 Applying MCP Server fixes..."
echo "==============================================="

cd /Users/joe/dev/mcp_cm_v1/enhanced-deployment

echo "📦 Stopping containers..."
docker-compose down

echo "🚀 Rebuilding MCP server with clean cache..."
docker-compose build --no-cache mcp-server

if [ $? -eq 0 ]; then
    echo "✅ Build successful!"
    
    echo "🏃 Starting containers..."
    docker-compose up -d
    
    echo "⏱️  Waiting for services to start..."
    sleep 10
    
    echo "🔍 Checking container status..."
    docker-compose ps
    
    echo "📋 Checking MCP server logs..."
    docker-compose logs mcp-server --tail=20
    
    echo ""
    echo "✅ MCP Server fix applied successfully!"
    echo ""
    echo "🔧 What was fixed:"
    echo "   • Fixed dependency conflict (starlette version compatibility)"
    echo "   • Updated to use FastMCP for HTTP streaming"
    echo "   • Fixed imports and API compatibility"
    echo "   • Updated Dockerfile for consistency"
    echo ""
    echo "🌐 MCP Server should now be running on: http://localhost:8090"
    echo "📊 Check if it's working:"
    echo "   curl http://localhost:8090/"
    echo ""
else
    echo "❌ Build failed. Check the error messages above."
    echo "🔧 Try these troubleshooting steps:"
    echo "   1. Check the requirements.txt file"
    echo "   2. Verify Docker has enough resources"
    echo "   3. Check if there are any missing dependencies"
fi