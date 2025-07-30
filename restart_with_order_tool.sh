#!/bin/bash
# Restart enhanced services to activate order_management MCP tool

echo "🔄 Restarting Enhanced Services to Activate Order Management Tool"
echo "=============================================================="

# Stop current services
echo "Stopping enhanced services..."
docker-compose -f docker-compose.extended.yml down

# Wait a moment
sleep 5

# Rebuild MCP server with new tool
echo "Rebuilding MCP server with order management tool..."
docker-compose -f docker-compose.extended.yml build --no-cache mcp-server

# Start services again
echo "Starting enhanced services with order management tool..."
docker-compose -f docker-compose.extended.yml up -d

# Wait for services to start
echo "Waiting for services to initialize..."
sleep 20

# Check health
echo "Checking service health..."

# Check PostgreSQL
if docker exec telecom_postgres pg_isready -U telecom_user -d telecom_catalog &>/dev/null; then
    echo "✅ PostgreSQL is healthy"
else
    echo "❌ PostgreSQL is not ready"
fi

# Check Catalog Manager
if curl -f http://localhost:8080/health &>/dev/null; then
    echo "✅ Catalog Manager is healthy"
else
    echo "❌ Catalog Manager is not ready"
fi

# Test MCP tools endpoint
echo ""
echo "🧪 Testing MCP Tools Endpoint..."
curl -X POST http://localhost:8090/mcp/stream \
    -H "Content-Type: application/json" \
    -H "Accept: application/json-stream" \
    -d '{"jsonrpc": "2.0", "method": "tools/list", "params": {}, "id": 1}' 2>/dev/null | jq '.result.tools[] | select(.name == "order_management") | .name' || echo "❌ Order management tool not found"

# Test the TMF622 order endpoint directly
echo ""
echo "Testing TMF622 order endpoint directly:"
curl -s "http://localhost:8080/tmf622/productOrder?limit=3" | jq '. | length' 2>/dev/null || echo "❌ TMF622 endpoint failed"

echo ""
echo "🎉 Services restarted! New MCP tools available:"
echo ""
echo "📊 New MCP Tool:"
echo "• order_management() - List all recent orders"
echo "• order_management(customerId='8452935') - Orders by customer"
echo "• order_management(orderId='order-id-here') - Specific order"
echo ""
echo "📁 New MCP Resources:"
echo "• orders://recent - Browse recent orders"
echo "• orders://customer/{customer_id} - Browse customer orders"
echo ""
echo "🔗 API Endpoints:"
echo "• GET /tmf622/productOrder - List orders (TMF622 standard)"
echo "• GET /tmf622/productOrder?relatedParty.id=8452935 - Customer orders"
echo "• GET /tmf622/productOrder/{orderId} - Specific order"
echo ""
echo "🤖 Ready to use: Try 'list recent orders' or 'order_management()'"
echo ""
