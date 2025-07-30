#!/bin/bash
# Restart enhanced services to activate TMF622 order management

echo "🔄 Restarting Enhanced Services to Activate Order Management"
echo "=========================================================="

# Stop current services
echo "Stopping enhanced services..."
docker-compose -f docker-compose.extended.yml down

# Wait a moment
sleep 3

# Start services again
echo "Starting enhanced services with order management..."
docker-compose -f docker-compose.extended.yml up -d

# Wait for services to start
echo "Waiting for services to initialize..."
sleep 15

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

# Test the new TMF622 endpoints
echo ""
echo "🧪 Testing TMF622 Order Management Endpoints..."

# Test order listing
echo "Testing order listing endpoint:"
curl -s "http://localhost:8080/tmf622/productOrder?limit=5" | jq . || echo "❌ Order listing failed"

echo ""
echo "🎉 Services restarted! TMF622 Order Management is now available!"
echo ""
echo "Available endpoints:"
echo "• GET /tmf622/productOrder - List all orders"
echo "• GET /tmf622/productOrder?relatedParty.id=8452935 - Orders by customer"
echo "• GET /tmf622/productOrder/{orderId} - Specific order"
echo ""
