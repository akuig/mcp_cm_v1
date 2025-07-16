#!/bin/bash

echo "🔧 Fixing MCP Server to match agent expectations..."
echo "   • Switching to port 8090 (from 8081)"
echo "   • Adding /mcp/stream endpoint"
echo "   • Adding 8 new catalog management tools"

# Stop the current MCP server
docker-compose stop mcp-server

# Remove the old MCP server image to force rebuild
docker rmi enhanced-deployment-mcp-server:latest 2>/dev/null || true

echo "✅ Stopped old MCP server"

# Rebuild and restart the MCP server with new configuration
echo "🚀 Rebuilding Enhanced MCP server with 12 tools..."
docker-compose up -d --build mcp-server

echo "⏳ Waiting for MCP server to start on port 8090..."
sleep 15

# Test the endpoints that your agent expects
echo "🧪 Testing agent endpoints..."

# Test health endpoint
if curl -f http://localhost:8090/health &>/dev/null; then
    echo "✅ Health endpoint responding on port 8090"
else
    echo "❌ Health endpoint not responding"
fi

# Test MCP info endpoint
if curl -f http://localhost:8090/mcp &>/dev/null; then
    echo "✅ MCP info endpoint responding"
else
    echo "❌ MCP info endpoint not responding"
fi

# Test that the /mcp/stream endpoint exists (it should accept POST)
if curl -f -X POST http://localhost:8090/mcp/stream -H "Content-Type: application/json" -d '{"jsonrpc":"2.0","method":"initialize","id":1}' &>/dev/null; then
    echo "✅ MCP stream endpoint responding to JSON-RPC"
else
    echo "⚠️  MCP stream endpoint may need proper JSON-RPC request"
fi

echo ""
echo "📊 Enhanced MCP Server Status:"
echo "================================"

# Check if container is running
if docker-compose ps mcp-server | grep -q "Up"; then
    echo "✅ MCP Server container is running"
    
    # Show the logs to verify startup
    echo ""
    echo "📋 Recent logs:"
    docker-compose logs --tail=10 mcp-server
    
    echo ""
    echo "🎯 Agent Connection Test:"
    echo "• Agent should connect to: http://localhost:8090/mcp/stream"
    echo "• Health check available at: http://localhost:8090/health"
    echo "• Server info available at: http://localhost:8090/mcp"
    echo ""
    echo "🛠️  Enhanced Tools Available (12 total):"
    echo "   Customer Tools (4): service_qualification, customer_management, product_ordering, service_activation"
    echo "   Catalog Tools (8): list_service_specifications, list_product_offerings, list_geographic_locations,"
    echo "                      sync_catalog_data, create_service_specification, create_product_offering,"
    echo "                      link_offering_to_specification, add_geographic_coverage"
else
    echo "❌ MCP Server container failed to start"
    echo "📋 Error logs:"
    docker-compose logs --tail=20 mcp-server
fi

echo ""
echo "🌐 All Services Status:"
docker-compose ps