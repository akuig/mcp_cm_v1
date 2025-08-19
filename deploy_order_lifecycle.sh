#!/bin/bash

# ============================================================================
# Deploy Order Lifecycle Management Tools for Telepath AI
# Adds TMF622-compliant order management: cancel, delete, update status
# ============================================================================

set -e  # Exit on error

echo "🚀 Deploying Order Lifecycle Management Tools..."
echo "=============================================="

# Navigate to project directory
cd /Users/joe/dev/mcp_cm_v1

# Step 1: Stop existing containers
echo ""
echo "📦 Step 1: Stopping existing containers..."
docker-compose down

# Step 2: Apply database changes
echo ""
echo "🗄️ Step 2: Applying database schema updates..."
echo "   - Adding order_status_history table"
echo "   - Adding updated_at column to orders table"

# Create temporary SQL file for the updates
cat > temp_order_updates.sql << 'EOF'
-- Connect to the database
\c telecom_catalog;

-- Add updated_at column to orders table if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'orders' AND column_name = 'updated_at'
    ) THEN
        ALTER TABLE orders ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
    END IF;
END $$;

-- Create order_status_history table if it doesn't exist
CREATE TABLE IF NOT EXISTS order_status_history (
    id SERIAL PRIMARY KEY,
    order_id VARCHAR(50) REFERENCES orders(id) ON DELETE CASCADE,
    status VARCHAR(50) NOT NULL,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reason TEXT,
    changed_by VARCHAR(100)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_order_status_history_order ON order_status_history(order_id);
CREATE INDEX IF NOT EXISTS idx_order_status_history_changed ON order_status_history(changed_at);

-- Insert initial status history for existing orders
INSERT INTO order_status_history (order_id, status, reason)
SELECT id, status, 'Initial order status'
FROM orders
WHERE NOT EXISTS (
    SELECT 1 FROM order_status_history 
    WHERE order_status_history.order_id = orders.id
);

-- Grant permissions
GRANT ALL PRIVILEGES ON order_status_history TO telecom_user;
GRANT USAGE, SELECT ON SEQUENCE order_status_history_id_seq TO telecom_user;
EOF

# Step 3: Start only the database container
echo ""
echo "🐘 Step 3: Starting PostgreSQL container..."
docker-compose up -d postgres

# Wait for PostgreSQL to be ready
echo "   Waiting for PostgreSQL to be ready..."
sleep 5

# Apply the database updates
echo "   Applying database updates..."
docker exec -i telecom_postgres psql -U telecom_user -d telecom_catalog < temp_order_updates.sql

# Clean up temporary file
rm temp_order_updates.sql

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
sleep 10

# Step 6: Verify deployment
echo ""
echo "✅ Step 6: Verifying deployment..."

# Check if services are running
echo ""
echo "Checking service status..."
docker-compose ps

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
echo "==============================================