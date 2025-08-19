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
