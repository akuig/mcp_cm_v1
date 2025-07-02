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
-- Create tables
CREATE TABLE IF NOT EXISTS customers (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    account_status VARCHAR(50) NOT NULL,
    credit_score INTEGER,
    has_overdue_payments BOOLEAN DEFAULT FALSE,
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
INSERT INTO customers (id, name, account_status, credit_score, has_overdue_payments) VALUES
('8452934', 'Jane Doe', 'active', 720, false),
('8452935', 'John Smith', 'active', 650, true),
('8452936', 'Alice Johnson', 'active', 780, false),
('8452937', 'Bob Williams', 'suspended', 550, true)
ON CONFLICT (id) DO NOTHING;

INSERT INTO service_coverage (street_name, city, service_type, max_speed_mbps) VALUES
('Main Street', 'Springfield', 'fiber', 1000),
('Oak Avenue', 'Springfield', 'fiber', 1000),
('Elm Street', 'Springfield', 'cable', 200),
('Pine Road', 'Springfield', 'dsl', 50),
('Maple Drive', 'Springfield', 'fiber', 500),
('Cherry Lane', 'Shelbyville', 'cable', 100);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_customers_status ON customers(account_status);
CREATE INDEX IF NOT EXISTS idx_coverage_location ON service_coverage(street_name, city);
CREATE INDEX IF NOT EXISTS idx_orders_customer ON orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);

-- Verify data
SELECT COUNT(*) as customer_count FROM customers;
SELECT COUNT(*) as coverage_count FROM service_coverage;
EOF

echo ""
echo "✅ Database initialized successfully!"
echo ""
echo "Now start all services:"
echo "docker-compose up -d"
