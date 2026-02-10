#!/bin/bash
# Reset and initialize the database

echo "Resetting database..."

# Stop services
docker-compose down

# Remove old data
docker volume rm mcp_cm_v1_postgres_data 2>/dev/null || true

# Start only postgres
docker-compose up -d postgres

# Wait for postgres to be ready
echo "Waiting for PostgreSQL to start..."
sleep 10

# Initialize the database directly
echo "Creating tables and inserting demo data..."
docker exec -i telecom_postgres psql -U telecom_user -d telecom_catalog << 'EOF'
-- Clear existing data (order matters due to foreign keys)
DELETE FROM order_addresses;
DELETE FROM activation_addresses;
DELETE FROM orders;
DELETE FROM service_activations;
DELETE FROM service_coverage;
DELETE FROM customers;
DELETE FROM service_specifications;

-- Create tables
CREATE TABLE IF NOT EXISTS service_specifications (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    service_type VARCHAR(50) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS customers (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    account_status VARCHAR(50) NOT NULL,
    credit_score INTEGER,
    has_overdue_payments BOOLEAN DEFAULT FALSE,
    street_number VARCHAR(20),
    street_name VARCHAR(200),
    city VARCHAR(100),
    postal_code VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS service_coverage (
    id SERIAL PRIMARY KEY,
    street_name VARCHAR(200) NOT NULL,
    city VARCHAR(100) NOT NULL,
    service_type VARCHAR(50) NOT NULL,
    max_speed_mbps INTEGER,
    available BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS orders (
    id VARCHAR(50) PRIMARY KEY,
    order_date DATE NOT NULL,
    external_id VARCHAR(100),
    customer_id VARCHAR(50) REFERENCES customers(id),
    product_offering_id VARCHAR(50),
    status VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS order_addresses (
    id SERIAL PRIMARY KEY,
    order_id VARCHAR(50) REFERENCES orders(id),
    street_number VARCHAR(20),
    street_name VARCHAR(200),
    city VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS service_activations (
    id VARCHAR(50) PRIMARY KEY,
    service_name VARCHAR(200),
    service_type VARCHAR(50),
    service_specification_id VARCHAR(50),
    status VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS activation_addresses (
    id SERIAL PRIMARY KEY,
    activation_id VARCHAR(50) REFERENCES service_activations(id),
    street_number VARCHAR(20),
    street_name VARCHAR(200),
    city VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert demo data
-- Service Specifications
INSERT INTO service_specifications (id, name, service_type, description) VALUES
('fiber500', 'Fiber 500 Mbps Plan', 'broadband', '500 Mbps fiber internet service'),
('fiber1000', 'Fiber 1 Gbps Plan', 'broadband', '1 Gbps fiber internet service'),
('cable200', 'Cable 200 Mbps Plan', 'broadband', '200 Mbps cable internet service'),
('dsl50', 'DSL 50 Mbps Plan', 'broadband', '50 Mbps DSL internet service'),
('tv_basic', 'Basic TV Package', 'tv', '50+ channels including local and news'),
('tv_premium', 'Premium TV Package', 'tv', '200+ channels including sports and movies'),
('tv_ultimate', 'Ultimate TV Package', 'tv', '400+ channels with all premium content'),
('mobile_5gb', 'Mobile 5GB Plan', 'mobile', '5GB monthly data with unlimited calls/texts'),
('mobile_25gb', 'Mobile 25GB Plan', 'mobile', '25GB monthly data with unlimited calls/texts'),
('mobile_unlimited', 'Mobile Unlimited Plan', 'mobile', 'Unlimited 5G data, calls, and texts'),
('wireless_50', 'Wireless Broadband 50 Mbps', 'wireless_broadband', '50 Mbps wireless internet'),
('wireless_150', 'Wireless Broadband 150 Mbps', 'wireless_broadband', '150 Mbps 5G wireless internet')
ON CONFLICT (id) DO NOTHING;

-- Customers
INSERT INTO customers (id, name, account_status, credit_score, has_overdue_payments, street_number, street_name, city, postal_code) VALUES
('8452934', 'Jane Doe', 'active', 720, false, '456', 'Main Street', 'Springfield', '01101'),
('8452935', 'John Smith', 'active', 650, true, '123', 'Main Street', 'Springfield', '01101'),
('8452936', 'Alice Johnson', 'active', 780, false, '789', 'Oak Avenue', 'Springfield', '01102'),
('8452937', 'Bob Williams', 'suspended', 550, true, '321', 'Elm Street', 'Springfield', '01103')
ON CONFLICT (id) DO NOTHING;

INSERT INTO service_coverage (street_name, city, service_type, max_speed_mbps) VALUES
('Main Street', 'Springfield', 'fiber', 1000),
('Main Street', 'Springfield', 'tv', NULL),
('Main Street', 'Springfield', 'mobile', NULL),
('Main Street', 'Springfield', 'wireless_broadband', 150),
('Oak Avenue', 'Springfield', 'fiber', 1000),
('Oak Avenue', 'Springfield', 'tv', NULL),
('Oak Avenue', 'Springfield', 'mobile', NULL),
('Oak Avenue', 'Springfield', 'wireless_broadband', 150),
('Elm Street', 'Springfield', 'cable', 200),
('Elm Street', 'Springfield', 'tv', NULL),
('Elm Street', 'Springfield', 'mobile', NULL),
('Pine Road', 'Springfield', 'dsl', 50),
('Pine Road', 'Springfield', 'tv', NULL),
('Pine Road', 'Springfield', 'mobile', NULL),
('Maple Drive', 'Springfield', 'fiber', 500),
('Maple Drive', 'Springfield', 'tv', NULL),
('Cherry Lane', 'Shelbyville', 'cable', 100),
('Cherry Lane', 'Shelbyville', 'tv', NULL),
('Cherry Lane', 'Shelbyville', 'mobile', NULL);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_customers_status ON customers(account_status);
CREATE INDEX IF NOT EXISTS idx_coverage_location ON service_coverage(street_name, city);
CREATE INDEX IF NOT EXISTS idx_orders_customer ON orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);

-- Verify data
SELECT COUNT(*) as customer_count FROM customers;
SELECT COUNT(*) as coverage_count FROM service_coverage;
SELECT COUNT(*) as order_count FROM orders;
EOF

echo ""
echo "✅ Database initialized successfully!"
echo ""
echo "Now start all services:"
echo "docker-compose up -d"
