#!/bin/bash

# Quick verification script for order lifecycle deployment

echo "🔍 Verifying Order Lifecycle Deployment"
echo "========================================"

# Check if PostgreSQL is running
echo ""
echo "1. Checking PostgreSQL..."
if docker ps | grep -q telecom_postgres; then
    echo "   ✅ PostgreSQL is running"
    
    # Check database exists
    if docker exec telecom_postgres psql -U telecom_user -d telecom_catalog -c "SELECT 1" > /dev/null 2>&1; then
        echo "   ✅ telecom_catalog database exists"
        
        # Check tables
        echo ""
        echo "2. Checking database tables..."
        
        # Check orders table
        if docker exec telecom_postgres psql -U telecom_user -d telecom_catalog -c "\d orders" | grep -q "updated_at"; then
            echo "   ✅ orders table has updated_at column"
        else
            echo "   ❌ orders table missing updated_at column"
        fi
        
        # Check order_status_history table
        if docker exec telecom_postgres psql -U telecom_user -d telecom_catalog -c "\dt" | grep -q "order_status_history"; then
            echo "   ✅ order_status_history table exists"
        else
            echo "   ❌ order_status_history table missing"
        fi
    else
        echo "   ❌ telecom_catalog database not accessible"
    fi
else
    echo "   ❌ PostgreSQL is not running"
fi

# Check if Catalog Manager is running
echo ""
echo "3. Checking Catalog Manager..."
if docker ps | grep -q catalog-manager; then
    echo "   ✅ Catalog Manager is running"
    
    # Test health endpoint
    if curl -s http://localhost:8080/health | grep -q "healthy"; then
        echo "   ✅ Catalog Manager API is responsive"
    else
        echo "   ⚠️  Catalog Manager API not responding on port 8080"
    fi
else
    echo "   ❌ Catalog Manager is not running"
fi

# Check if MCP Server is running
echo ""
echo "4. Checking MCP Server..."
if docker ps | grep -q mcp_server; then
    echo "   ✅ MCP Server is running"
else
    echo "   ❌ MCP Server is not running"
fi

# Test new endpoints
echo ""
echo "5. Testing new order endpoints..."

# Create a test order
echo "   Creating test order..."
TEST_RESPONSE=$(curl -s -X POST http://localhost:8080/tmf622/productOrder \
  -H "Content-Type: application/json" \
  -d '{
    "orderDate": "'$(date +%Y-%m-%d)'",
    "externalId": "VERIFY_TEST_'$(date +%s)'",
    "relatedParty": [{"id": "8452934", "role": "customer"}],
    "orderItem": [{
      "action": "add",
      "productOffering": {"id": "pkg_fiber_500"},
      "product": {
        "place": {
          "streetNumber": "456",
          "streetName": "Main Street",
          "city": "Springfield"
        }
      }
    }]
  }' 2>/dev/null)

if echo "$TEST_RESPONSE" | grep -q '"id"'; then
    ORDER_ID=$(echo "$TEST_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('id', ''))" 2>/dev/null)
    if [ ! -z "$ORDER_ID" ]; then
        echo "   ✅ Order creation works (ID: $ORDER_ID)"
        
        # Test status update
        if curl -s -X PATCH "http://localhost:8080/tmf622/productOrder/$ORDER_ID" \
          -H "Content-Type: application/json" \
          -d '{"state": "acknowledged"}' | grep -q "acknowledged"; then
            echo "   ✅ Order status update works"
        else
            echo "   ❌ Order status update failed"
        fi
        
        # Test cancel
        if curl -s -X POST "http://localhost:8080/tmf622/productOrder/$ORDER_ID/cancel" | grep -q "cancelled"; then
            echo "   ✅ Order cancellation works"
        else
            echo "   ❌ Order cancellation failed"
        fi
        
        # Test delete
        if curl -s -X DELETE "http://localhost:8080/tmf622/productOrder/$ORDER_ID" | grep -q "deleted"; then
            echo "   ✅ Order deletion works"
        else
            echo "   ❌ Order deletion failed"
        fi
    else
        echo "   ❌ Could not extract order ID"
    fi
else
    echo "   ❌ Order creation failed"
fi

echo ""
echo "========================================"
echo "Verification complete!"
echo ""
echo "If any checks failed, run:"
echo "  ./fix_database_and_deploy.sh"
echo ""