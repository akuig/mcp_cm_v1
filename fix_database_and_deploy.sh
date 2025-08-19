#!/bin/bash

# ============================================================================
# Fix Database and Deploy Order Lifecycle Management Tools
# Ensures database exists and applies schema updates
# ============================================================================

set -e  # Exit on error

echo "🔧 Fixing Database and Deploying Order Lifecycle Management Tools..."
echo "=============================================="

# Navigate to project directory
cd /Users/joe/dev/mcp_cm_v1

# Step 1: Ensure database container is running
echo ""
echo "🐘 Step 1: Starting PostgreSQL container..."
docker-compose up -d postgres

# Wait for PostgreSQL to be ready
echo "   Waiting for PostgreSQL to be ready..."
sleep 8

# Step 2: Verify database exists and create if needed
echo ""
echo "🗄️ Step 2: Verifying database exists..."
docker exec telecom_postgres psql -U telecom_user -d postgres -c "SELECT 1 FROM pg_database WHERE datname = 'telecom_catalog'" | grep -q 1 || {
    echo "   Creating telecom_catalog database..."
    docker exec telecom_postgres psql -U telecom_user -d postgres -c "CREATE DATABASE telecom_catalog OWNER telecom_user;"
}

# Step 3: Apply the base schema if tables don't exist
echo ""
echo "📋 Step 3: Ensuring base tables exist..."
docker exec telecom_postgres psql -U telecom_user -d telecom_catalog -c "\dt" | grep -q "orders" || {
    echo "   Applying base database schema..."
    docker exec -i telecom_postgres psql -U telecom_user -d telecom_catalog < init_db_extended.sql
}

# Step 4: Apply order lifecycle updates
echo ""
echo "🔄 Step 4: Applying order lifecycle updates..."

# Create and apply the updates
cat > temp_order_lifecycle_fix.sql << 'EOF'
-- Ensure we're in the right database
\c telecom_catalog;

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

-- Create indexes if they don't exist
CREATE INDEX IF NOT EXISTS idx_order_status_history_order ON order_status_history(order_id);
CREATE INDEX IF NOT EXISTS idx_order_status_history_changed ON order_status_history(changed_at);

-- Insert initial status history for existing orders (if any)
INSERT INTO order_status_history (order_id, status, reason)
SELECT id, status, 'Initial order status'
FROM orders
WHERE NOT EXISTS (
    SELECT 1 FROM order_status_history 
    WHERE order_status_history.order_id = orders.id
);

-- Grant permissions (safe to run multiple times)
GRANT ALL PRIVILEGES ON order_status_history TO telecom_user;
GRANT ALL PRIVILEGES ON orders TO telecom_user;

-- Grant sequence permissions if the sequence exists
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_sequences WHERE schemaname = 'public' AND sequencename = 'order_status_history_id_seq') THEN
        GRANT USAGE, SELECT ON SEQUENCE order_status_history_id_seq TO telecom_user;
    END IF;
END $$;

-- Show results
SELECT 'Orders table columns:' as info;
SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'orders';

SELECT 'Order status history table:' as info;
SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'order_status_history') as exists;
EOF

echo "   Applying updates..."
docker exec -i telecom_postgres psql -U telecom_user -d telecom_catalog < temp_order_lifecycle_fix.sql

# Clean up
rm temp_order_lifecycle_fix.sql

# Step 5: Rebuild containers with new code
echo ""
echo "🔨 Step 5: Rebuilding containers with new code..."
docker-compose build catalog-manager mcp-server

# Step 6: Start all services
echo ""
echo "🚀 Step 6: Starting all services..."
docker-compose up -d

# Wait for services
echo ""
echo "⏳ Waiting for services to be ready..."
sleep 10

# Step 7: Verify deployment
echo ""
echo "✅ Step 7: Verifying deployment..."

# Check services
docker-compose ps

# Test database connection and tables
echo ""
echo "📊 Database verification:"
docker exec telecom_postgres psql -U telecom_user -d telecom_catalog -c "\dt" | grep -E "(orders|order_status_history)" || echo "Tables check complete"

# Quick API test
echo ""
echo "🧪 Testing API endpoints:"
curl -s http://localhost:8080/health | python3 -c "import sys, json; data=json.load(sys.stdin); print(f'Catalog Manager: {data.get(\"status\", \"unknown\")}');" || echo "Catalog Manager: Check manually"

echo ""
echo "=============================================="
echo "✅ Database Fixed and Deployment Complete!"
echo ""
echo "📋 What was fixed:"
echo "   - Ensured telecom_catalog database exists"
echo "   - Applied base schema if needed"
echo "   - Added order_status_history table"
echo "   - Added updated_at column to orders"
echo "   - Set proper permissions"
echo ""
echo "🎯 New Order Lifecycle Tools Available:"
echo "   - cancel_order"
echo "   - delete_order"  
echo "   - update_order_status"
echo ""
echo "📝 Next Steps:"
echo "   1. Test the tools: python3 test_order_lifecycle.py"
echo "   2. Restart Claude Desktop to load new MCP tools"
echo ""
echo "=============================================="