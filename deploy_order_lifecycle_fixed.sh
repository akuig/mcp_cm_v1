#!/bin/bash

# ============================================================================
# Deploy Order Lifecycle Management Tools for Telepath AI - FIXED VERSION
# Adds TMF622-compliant order management: cancel, delete, update status
# ============================================================================

set -e  # Exit on error

echo "🚀 Deploying Order Lifecycle Management Tools (Fixed)..."
echo "=============================================="

# Navigate to project directory
cd /Users/joe/dev/mcp_cm_v1

# Step 1: Stop existing containers
echo ""
echo "📦 Step 1: Stopping existing containers..."
docker-compose down

# Step 2: Start only the database container
echo ""
echo "🐘 Step 2: Starting PostgreSQL container..."
docker-compose up -d postgres

# Wait for PostgreSQL to be ready
echo "   Waiting for PostgreSQL to be ready..."
for i in {1..10}; do
    if docker exec telecom_postgres pg_isready -U telecom_user > /dev/null 2>&1; then
        echo "   PostgreSQL is ready!"
        break
    fi
    echo "   Waiting... ($i/10)"
    sleep 2
done

# Step 3: Apply database changes
echo ""
echo "🗄️ Step 3: Applying database schema updates..."
echo "   - Adding order_status_history table"
echo "   - Adding updated_at column to orders table"

# Apply database updates directly without temporary file
docker exec telecom_postgres psql -U telecom_user -d telecom_catalog << 'EOF'
-- Add updated_at column to orders table if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'orders' AND column_name = 'updated_at'
    ) THEN
        ALTER TABLE orders ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
        RAISE NOTICE 'Added updated_at column to orders table';
    ELSE
        RAISE NOTICE 'updated_at column already exists';
    END IF;
END $$;

-- Create order_status_history table if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.tables 
        WHERE table_name = 'order_status_history'
    ) THEN
        CREATE TABLE order_status_history (
            id SERIAL PRIMARY KEY,
            order_id VARCHAR(50) REFERENCES orders(id) ON DELETE CASCADE,
            status VARCHAR(50) NOT NULL,
            changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            reason TEXT,
            changed_by VARCHAR(100)
        );
        RAISE NOTICE 'Created order_status_history table';
    ELSE
        RAISE NOTICE 'order_status_history table already exists';
    END IF;
END $$;

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_order_status_history_order ON order_status_history(order_id);
CREATE INDEX IF NOT EXISTS idx_order_status_history_changed ON order_status_history(changed_at);

-- Insert initial status history for existing orders (only if not already present)
INSERT INTO order_status_history (order_id, status, reason)
SELECT id, status, 'Initial order status'
FROM orders o
WHERE NOT EXISTS (
    SELECT 1 FROM order_status_history 
    WHERE order_status_history.order_id = o.id
);

-- Grant permissions
GRANT ALL PRIVILEGES ON order_status_history TO telecom_user;
GRANT USAGE, SELECT ON SEQUENCE order_status_history_id_seq TO telecom_user;

-- Show results
SELECT 'Database updates completed successfully' as status;
EOF

if [ $? -eq 0 ]; then
    echo "   ✅ Database updates applied successfully"
else
    echo "   ❌ Failed to apply database updates"
    exit 1
fi

# Step 4: Rebuild the containers with new code
echo ""
echo "🔨 Step 4: Rebuilding containers with new code..."
docker-compose build --no-cache catalog-manager mcp-server

# Step 5: Start all services
echo ""
echo "🚀 Step 5: Starting all services..."
docker-compose up -d

# Wait for services to be ready
echo ""
echo "⏳ Waiting for services to be ready..."
for i in {1..15}; do
    if curl -s http://localhost:8080/health > /dev/null 2>&1; then
        echo "   Catalog Manager is ready!"
        break
    fi
    echo "   Waiting for services... ($i/15)"
    sleep 2
done

# Step 6: Verify deployment
echo ""
echo "✅ Step 6: Verifying deployment..."

# Check if services are running
echo ""
echo "Checking service status..."
docker-compose ps

# Quick health check
echo ""
echo "Health check:"
curl -s http://localhost:8080/health | python3 -m json.tool || echo "Health check failed"

# Step 7: Test the new endpoints (optional)
echo ""
echo "🧪 Step 7: Quick endpoint test..."

# Create a test order
echo "Creating test order..."
TEST_RESPONSE=$(curl -s -X POST http://localhost:8080/tmf622/productOrder \
  -H "Content-Type: application/json" \
  -d '{
    "orderDate": "'$(date +%Y-%m-%d)'",
    "externalId": "TEST_DEPLOYMENT_'$(date +%s)'",
    "relatedParty": [{
      "id": "8452934",
      "role": "customer"
    }],
    "orderItem": [{
      "action": "add",
      "productOffering": {
        "id": "pkg_fiber_500"
      },
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
    TEST_ORDER_ID=$(echo "$TEST_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('id', ''))" 2>/dev/null)
    if [ ! -z "$TEST_ORDER_ID" ]; then
        echo "✅ Test order created: $TEST_ORDER_ID"
        
        # Test cancel endpoint
        echo "Testing cancel endpoint..."
        CANCEL_RESPONSE=$(curl -s -X POST "http://localhost:8080/tmf622/productOrder/$TEST_ORDER_ID/cancel" 2>/dev/null)
        if echo "$CANCEL_RESPONSE" | grep -q "cancelled"; then
            echo "✅ Cancel endpoint working"
        fi
        
        # Test delete endpoint
        echo "Testing delete endpoint..."
        DELETE_RESPONSE=$(curl -s -X DELETE "http://localhost:8080/tmf622/productOrder/$TEST_ORDER_ID" 2>/dev/null)
        if echo "$DELETE_RESPONSE" | grep -q "deleted"; then
            echo "✅ Delete endpoint working"
        fi
    fi
else
    echo "⚠️  Could not create test order - manual testing required"
fi

echo ""
echo "=============================================="
echo "✅ Deployment Complete!"
echo ""
echo "📊 Summary:"
echo "   - Enhanced Catalog Manager with order lifecycle management"
echo "   - Added 3 new TMF622-compliant tools:"
echo "     • cancel_order - Cancel orders"
echo "     • delete_order - Permanently delete orders"
echo "     • update_order_status - Update order states"
echo "   - Total MCP tools available: 16"
echo ""
echo "📝 Next Steps:"
echo "   1. Restart Claude Desktop to load the new tools"
echo "   2. Test: python3 test_order_lifecycle.py"
echo "   3. Use for demo reset: cancel/delete Jane Doe's orders"
echo ""
echo "🌐 Service URLs:"
echo "   - Catalog Manager: http://localhost:8080"
echo "   - MCP Server: http://localhost:8090"
echo ""
echo "📋 Troubleshooting:"
echo "   - Check logs: docker logs catalog-manager"
echo "   - Check DB: docker exec telecom_postgres psql -U telecom_user -d telecom_catalog"
echo ""
echo "=============================================="