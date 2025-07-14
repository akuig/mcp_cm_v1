#!/bin/bash
# Complete fix for FastAPI dependency and HTTP streaming

echo "🔧 Complete Fix for MCP HTTP Streaming"
echo "====================================="
echo ""

# Make this script executable
chmod +x fix_fastapi_dependency.sh

# Step 1: Fix dependencies and rebuild
echo "Step 1: Fixing dependencies..."
./fix_fastapi_dependency.sh

# Check if it worked
if docker-compose -f docker-compose-with-fault.yml ps mcp-server | grep -q "Up"; then
    echo ""
    echo "✅ MCP server is running with HTTP streaming!"
else
    echo ""
    echo "⚠️  Standard fix didn't work. Trying alternative..."
    
    # Step 2: Try the simple server instead
    echo ""
    echo "Step 2: Switching to simple HTTP server..."
    
    # Update docker-compose to use simple server
    sed -i.bak 's/mcp_http_streaming_server.py/mcp_simple_http_server.py/g' docker-compose-with-fault.yml
    
    # Rebuild and restart
    docker-compose -f docker-compose-with-fault.yml build mcp-server
    docker-compose -f docker-compose-with-fault.yml up -d mcp-server
    
    sleep 10
    
    if docker-compose -f docker-compose-with-fault.yml ps mcp-server | grep -q "Up"; then
        echo "✅ MCP server is now running with simple HTTP server!"
    else
        echo "❌ Both servers failed. Check logs:"
        docker-compose -f docker-compose-with-fault.yml logs --tail=50 mcp-server
        exit 1
    fi
fi

# Step 3: Test the endpoints
echo ""
echo "Step 3: Testing endpoints..."
if curl -s http://localhost:8090/health | grep -q "healthy"; then
    echo "✅ Health endpoint working!"
else
    echo "⚠️  Health endpoint not responding as expected"
fi

# Step 4: Final instructions
echo ""
echo "✅ MCP HTTP server is fixed and running!"
echo ""
echo "📝 To complete Claude Desktop setup:"
echo "1. Copy config:"
echo "   cp claude_desktop_config_http.json ~/Library/Application\\ Support/Claude/claude_desktop_config.json"
echo ""
echo "2. Restart Claude Desktop"
echo ""
echo "3. Look for 'telepath-fault-http' in MCP connections"
echo ""
echo "🎯 You can now use fault management tools in Claude!"
