-- Database initialization script for Telecom Catalog Demo

-- Use the database
\c telecom_catalog;

-- Create tables if not exists
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

-- Fault Management Tables
CREATE TABLE IF NOT EXISTS network_alarms (
    id VARCHAR(50) PRIMARY KEY,
    alarm_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    severity_order INTEGER NOT NULL,
    affected_location VARCHAR(200),
    description TEXT,
    impact_count INTEGER DEFAULT 0,
    status VARCHAR(50) NOT NULL,
    raised_time TIMESTAMP NOT NULL,
    acknowledged_at TIMESTAMP,
    cleared_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS trouble_tickets (
    id VARCHAR(50) PRIMARY KEY,
    customer_id VARCHAR(50) REFERENCES customers(id),
    description TEXT,
    severity VARCHAR(20),
    related_alarm_id VARCHAR(50) REFERENCES network_alarms(id),
    status VARCHAR(50) NOT NULL,
    resolution_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS remediation_actions (
    id VARCHAR(50) PRIMARY KEY,
    alarm_id VARCHAR(50) REFERENCES network_alarms(id),
    action_type VARCHAR(100),
    status VARCHAR(50),
    executed_at TIMESTAMP,
    completed_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS service_problems (
    id VARCHAR(50) PRIMARY KEY,
    description TEXT NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'open',
    severity VARCHAR(50) NOT NULL DEFAULT 'major',
    priority VARCHAR(50) NOT NULL DEFAULT 'high',
    affected_location VARCHAR(200),
    affected_service_type VARCHAR(50),
    impact_start_time TIMESTAMP,
    resolution TEXT,
    resolution_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert demo data

-- Service Specifications
INSERT INTO service_specifications (id, name, service_type, description) VALUES
-- Fiber Internet Services
('fiber_500', 'Fiber 500 Mbps', 'fiber_internet', '500 Mbps fiber internet service'),
('fiber_1000', 'Fiber 1 Gbps', 'fiber_internet', '1 Gbps fiber internet service'),
-- Cable Internet Services
('cable_100', 'Cable 100 Mbps', 'cable_internet', '100 Mbps cable internet service'),
('cable_200', 'Cable 200 Mbps', 'cable_internet', '200 Mbps cable internet service'),
-- DSL Internet Services
('dsl_50', 'DSL 50 Mbps', 'dsl_internet', '50 Mbps DSL internet service'),
-- Wireless Broadband Services
('wireless_50', 'Wireless 50 Mbps', 'wireless_broadband', '50 Mbps 5G wireless internet'),
('wireless_150', 'Wireless 150 Mbps', 'wireless_broadband', '150 Mbps 5G wireless internet'),
-- TV Services
('tv_basic', 'Basic TV Package', 'tv', '50+ channels including local and news'),
('tv_premium', 'Premium TV Package', 'tv', '200+ channels including sports and movies'),
('tv_ultimate', 'Ultimate TV Package', 'tv', '400+ channels with all premium content'),
-- Mobile Services
('mobile_5gb', 'Mobile 5GB Plan', 'mobile', '5GB monthly data with unlimited calls/texts'),
('mobile_25gb', 'Mobile 25GB Plan', 'mobile', '25GB monthly data with unlimited calls/texts'),
('mobile_unlimited', 'Mobile Unlimited Plan', 'mobile', 'Unlimited 5G data, calls, and texts');

-- Customers
INSERT INTO customers (id, name, account_status, credit_score, has_overdue_payments, street_number, street_name, city, postal_code) VALUES
('8452934', 'Jane Doe', 'active', 720, false, '456', 'Main Street', 'Springfield', '01101'),
('8452935', 'John Smith', 'active', 650, true, '123', 'Main Street', 'Springfield', '01101'),
('8452936', 'Alice Johnson', 'active', 780, false, '789', 'Oak Avenue', 'Springfield', '01102'),
('8452937', 'Bob Williams', 'suspended', 550, true, '321', 'Elm Street', 'Springfield', '01103');

-- Service Coverage
INSERT INTO service_coverage (street_name, city, service_type, max_speed_mbps) VALUES
-- Main Street, Springfield - Premium area with all services
('Main Street', 'Springfield', 'fiber_internet', 1000),
('Main Street', 'Springfield', 'wireless_broadband', 150),
('Main Street', 'Springfield', 'tv', NULL),
('Main Street', 'Springfield', 'mobile', NULL),
-- Oak Avenue, Springfield - Premium area with all services
('Oak Avenue', 'Springfield', 'fiber_internet', 1000),
('Oak Avenue', 'Springfield', 'wireless_broadband', 150),
('Oak Avenue', 'Springfield', 'tv', NULL),
('Oak Avenue', 'Springfield', 'mobile', NULL),
-- Elm Street, Springfield - Cable area
('Elm Street', 'Springfield', 'cable_internet', 200),
('Elm Street', 'Springfield', 'tv', NULL),
('Elm Street', 'Springfield', 'mobile', NULL),
-- Pine Road, Springfield - DSL area
('Pine Road', 'Springfield', 'dsl_internet', 50),
('Pine Road', 'Springfield', 'tv', NULL),
('Pine Road', 'Springfield', 'mobile', NULL),
-- Maple Drive, Springfield - Fiber area
('Maple Drive', 'Springfield', 'fiber_internet', 500),
('Maple Drive', 'Springfield', 'tv', NULL),
-- Cherry Lane, Shelbyville - Cable area
('Cherry Lane', 'Shelbyville', 'cable_internet', 100),
('Cherry Lane', 'Shelbyville', 'tv', NULL),
('Cherry Lane', 'Shelbyville', 'mobile', NULL);

-- Create indexes for performance
CREATE INDEX idx_customers_status ON customers(account_status);
CREATE INDEX idx_coverage_location ON service_coverage(street_name, city);
CREATE INDEX idx_orders_customer ON orders(customer_id);
CREATE INDEX idx_orders_status ON orders(status);
