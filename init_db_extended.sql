-- Extended Database initialization script for Telecom Catalog Demo
-- Includes new tables for product offerings, geographic locations, and catalog integrity

-- Use the database
\c telecom_catalog;

-- Create tables if not exists
CREATE TABLE IF NOT EXISTS service_specifications (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    service_type VARCHAR(50) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- New table for product offerings
CREATE TABLE IF NOT EXISTS product_offerings (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    category VARCHAR(50) NOT NULL,
    price_monthly DECIMAL(10,2),
    price_setup DECIMAL(10,2) DEFAULT 0,
    contract_length_months INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Junction table to link product offerings to service specifications
CREATE TABLE IF NOT EXISTS offering_service_links (
    id SERIAL PRIMARY KEY,
    product_offering_id VARCHAR(50) REFERENCES product_offerings(id) ON DELETE CASCADE,
    service_specification_id VARCHAR(50) REFERENCES service_specifications(id) ON DELETE CASCADE,
    is_primary BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(product_offering_id, service_specification_id)
);

-- Enhanced geographic locations table
CREATE TABLE IF NOT EXISTS geographic_locations (
    id SERIAL PRIMARY KEY,
    location_id VARCHAR(50) UNIQUE NOT NULL,
    street_number VARCHAR(20),
    street_name VARCHAR(200) NOT NULL,
    city VARCHAR(100) NOT NULL,
    state_province VARCHAR(100),
    postal_code VARCHAR(20),
    country VARCHAR(100) DEFAULT 'USA',
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    location_type VARCHAR(50) DEFAULT 'address',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Enhanced service coverage table with foreign key to geographic locations
CREATE TABLE IF NOT EXISTS service_coverage_new (
    id SERIAL PRIMARY KEY,
    location_id VARCHAR(50) REFERENCES geographic_locations(location_id),
    service_type VARCHAR(50) NOT NULL,
    max_speed_mbps INTEGER,
    available BOOLEAN DEFAULT TRUE,
    coverage_quality VARCHAR(20) DEFAULT 'good', -- excellent, good, fair, poor
    technology VARCHAR(50), -- fiber, cable, dsl, wireless, satellite
    signal_strength INTEGER, -- 1-5 scale for wireless
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Catalog integrity tracking
CREATE TABLE IF NOT EXISTS catalog_integrity (
    id SERIAL PRIMARY KEY,
    check_type VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL, -- passed, failed, warning
    message TEXT,
    details JSONB,
    checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sync operations log
CREATE TABLE IF NOT EXISTS sync_operations (
    id SERIAL PRIMARY KEY,
    operation_type VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL, -- running, completed, failed
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    records_processed INTEGER DEFAULT 0,
    errors_count INTEGER DEFAULT 0,
    details JSONB
);

-- Keep existing tables
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
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Order status history table for tracking order state changes
CREATE TABLE IF NOT EXISTS order_status_history (
    id SERIAL PRIMARY KEY,
    order_id VARCHAR(50) REFERENCES orders(id) ON DELETE CASCADE,
    status VARCHAR(50) NOT NULL,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reason TEXT,
    changed_by VARCHAR(100)
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

-- Service Specifications (enhanced)
INSERT INTO service_specifications (id, name, service_type, description) VALUES
-- Fiber Internet Services
('fiber_500', 'Fiber 500 Mbps', 'fiber_internet', '500 Mbps fiber internet service with 99.9% uptime SLA'),
('fiber_1000', 'Fiber 1 Gbps', 'fiber_internet', '1 Gbps fiber internet service with 99.9% uptime SLA'),
('fiber_2000', 'Fiber 2 Gbps', 'fiber_internet', '2 Gbps fiber internet service for power users'),
-- Cable Internet Services
('cable_100', 'Cable 100 Mbps', 'cable_internet', '100 Mbps cable internet service'),
('cable_200', 'Cable 200 Mbps', 'cable_internet', '200 Mbps cable internet service'),
('cable_400', 'Cable 400 Mbps', 'cable_internet', '400 Mbps cable internet service'),
-- DSL Internet Services
('dsl_25', 'DSL 25 Mbps', 'dsl_internet', '25 Mbps DSL internet service'),
('dsl_50', 'DSL 50 Mbps', 'dsl_internet', '50 Mbps DSL internet service'),
-- Wireless Broadband Services
('wireless_50', 'Wireless 50 Mbps', 'wireless_broadband', '50 Mbps 5G wireless internet'),
('wireless_150', 'Wireless 150 Mbps', 'wireless_broadband', '150 Mbps 5G wireless internet'),
('wireless_300', 'Wireless 300 Mbps', 'wireless_broadband', '300 Mbps 5G+ wireless internet'),
-- TV Services
('tv_basic', 'Basic TV Package', 'tv', '50+ channels including local and news'),
('tv_premium', 'Premium TV Package', 'tv', '200+ channels including sports and movies'),
('tv_ultimate', 'Ultimate TV Package', 'tv', '400+ channels with all premium content'),
('tv_streaming', 'Streaming TV Service', 'tv', 'Cloud-based TV streaming with 100+ channels'),
-- Mobile Services
('mobile_5gb', 'Mobile 5GB Plan', 'mobile', '5GB monthly data with unlimited calls/texts'),
('mobile_25gb', 'Mobile 25GB Plan', 'mobile', '25GB monthly data with unlimited calls/texts'),
('mobile_unlimited', 'Mobile Unlimited Plan', 'mobile', 'Unlimited 5G data, calls, and texts'),
-- Home Phone Services
('phone_basic', 'Basic Home Phone', 'phone', 'Unlimited local and long distance calling'),
('phone_international', 'International Home Phone', 'phone', 'Unlimited calling including international'),
-- Security Services
('security_basic', 'Basic Home Security', 'security', 'Door/window sensors with mobile monitoring'),
('security_premium', 'Premium Home Security', 'security', 'Full home security with cameras and professional monitoring');

-- Product Offerings
INSERT INTO product_offerings (id, name, description, category, price_monthly, price_setup, contract_length_months) VALUES
-- Internet Only Packages
('pkg_fiber_500', 'TeleCo Fiber 500', 'High-speed 500 Mbps fiber internet', 'internet', 59.99, 99.99, 12),
('pkg_fiber_1000', 'TeleCo Fiber Gig', 'Ultra-fast 1 Gbps fiber internet', 'internet', 79.99, 99.99, 12),
('pkg_fiber_2000', 'TeleCo Fiber Pro', 'Professional 2 Gbps fiber for power users', 'internet', 129.99, 199.99, 24),
('pkg_cable_400', 'TeleCo Cable Max', 'High-speed 400 Mbps cable internet', 'internet', 49.99, 49.99, 12),
('pkg_wireless_300', 'TeleCo 5G Home', 'Ultra-fast 5G+ wireless internet', 'internet', 69.99, 0.00, 0),

-- TV Only Packages
('pkg_tv_basic', 'TeleCo Basic TV', 'Essential TV package with local channels', 'tv', 29.99, 0.00, 12),
('pkg_tv_premium', 'TeleCo Premium TV', 'Premium TV with sports and movies', 'tv', 79.99, 49.99, 12),
('pkg_tv_streaming', 'TeleCo Stream TV', 'Next-gen streaming TV service', 'tv', 39.99, 0.00, 0),

-- Mobile Only Packages
('pkg_mobile_family', 'TeleCo Family Mobile', 'Family mobile plan with unlimited data', 'mobile', 120.00, 0.00, 24),
('pkg_mobile_unlimited', 'TeleCo Unlimited Mobile', 'Single line unlimited mobile', 'mobile', 65.00, 0.00, 0),

-- Bundle Packages
('pkg_triple_play', 'TeleCo Triple Play', 'Internet + TV + Phone bundle', 'bundle', 99.99, 99.99, 24),
('pkg_double_play_it', 'TeleCo Internet + TV', 'High-speed internet and premium TV', 'bundle', 89.99, 49.99, 12),
('pkg_smart_home', 'TeleCo Smart Home', 'Internet + TV + Security bundle', 'bundle', 119.99, 199.99, 24),
('pkg_everything', 'TeleCo Everything', 'Complete home connectivity solution', 'bundle', 149.99, 199.99, 24);

-- Link product offerings to service specifications
INSERT INTO offering_service_links (product_offering_id, service_specification_id, is_primary) VALUES
-- Internet packages
('pkg_fiber_500', 'fiber_500', true),
('pkg_fiber_1000', 'fiber_1000', true),
('pkg_fiber_2000', 'fiber_2000', true),
('pkg_cable_400', 'cable_400', true),
('pkg_wireless_300', 'wireless_300', true),

-- TV packages
('pkg_tv_basic', 'tv_basic', true),
('pkg_tv_premium', 'tv_premium', true),
('pkg_tv_streaming', 'tv_streaming', true),

-- Mobile packages
('pkg_mobile_family', 'mobile_unlimited', true),
('pkg_mobile_unlimited', 'mobile_unlimited', true),

-- Bundle packages - Triple Play
('pkg_triple_play', 'fiber_1000', true),
('pkg_triple_play', 'tv_premium', false),
('pkg_triple_play', 'phone_basic', false),

-- Bundle packages - Double Play
('pkg_double_play_it', 'fiber_500', true),
('pkg_double_play_it', 'tv_premium', false),

-- Bundle packages - Smart Home
('pkg_smart_home', 'fiber_1000', true),
('pkg_smart_home', 'tv_basic', false),
('pkg_smart_home', 'security_premium', false),

-- Bundle packages - Everything
('pkg_everything', 'fiber_2000', true),
('pkg_everything', 'tv_ultimate', false),
('pkg_everything', 'phone_international', false),
('pkg_everything', 'mobile_unlimited', false),
('pkg_everything', 'security_premium', false);

-- Geographic Locations
INSERT INTO geographic_locations (location_id, street_number, street_name, city, state_province, postal_code, latitude, longitude) VALUES
('loc_main_456', '456', 'Main Street', 'Springfield', 'MA', '01101', 42.1015, -72.5898),
('loc_main_123', '123', 'Main Street', 'Springfield', 'MA', '01101', 42.1018, -72.5895),
('loc_oak_789', '789', 'Oak Avenue', 'Springfield', 'MA', '01102', 42.1025, -72.5875),
('loc_elm_321', '321', 'Elm Street', 'Springfield', 'MA', '01103', 42.0995, -72.5920),
('loc_pine_101', '101', 'Pine Road', 'Springfield', 'MA', '01104', 42.0985, -72.5945),
('loc_maple_555', '555', 'Maple Drive', 'Springfield', 'MA', '01105', 42.1035, -72.5850),
('loc_cherry_777', '777', 'Cherry Lane', 'Shelbyville', 'MA', '01201', 42.2015, -72.4898);

-- Enhanced Service Coverage
INSERT INTO service_coverage_new (location_id, service_type, max_speed_mbps, coverage_quality, technology, signal_strength) VALUES
-- Main Street, Springfield - Premium fiber area
('loc_main_456', 'fiber_internet', 2000, 'excellent', 'fiber', NULL),
('loc_main_456', 'wireless_broadband', 300, 'excellent', '5G+', 5),
('loc_main_456', 'tv', NULL, 'excellent', 'fiber', NULL),
('loc_main_456', 'mobile', NULL, 'excellent', '5G', 5),
('loc_main_456', 'phone', NULL, 'excellent', 'voip', NULL),
('loc_main_456', 'security', NULL, 'excellent', 'wireless', 5),

('loc_main_123', 'fiber_internet', 2000, 'excellent', 'fiber', NULL),
('loc_main_123', 'wireless_broadband', 300, 'excellent', '5G+', 5),
('loc_main_123', 'tv', NULL, 'excellent', 'fiber', NULL),
('loc_main_123', 'mobile', NULL, 'excellent', '5G', 5),
('loc_main_123', 'phone', NULL, 'excellent', 'voip', NULL),

-- Oak Avenue, Springfield - Premium fiber area
('loc_oak_789', 'fiber_internet', 2000, 'excellent', 'fiber', NULL),
('loc_oak_789', 'wireless_broadband', 300, 'good', '5G', 4),
('loc_oak_789', 'tv', NULL, 'excellent', 'fiber', NULL),
('loc_oak_789', 'mobile', NULL, 'good', '5G', 4),
('loc_oak_789', 'security', NULL, 'good', 'wireless', 4),

-- Elm Street, Springfield - Cable area
('loc_elm_321', 'cable_internet', 400, 'good', 'cable', NULL),
('loc_elm_321', 'tv', NULL, 'good', 'cable', NULL),
('loc_elm_321', 'mobile', NULL, 'fair', '4G', 3),
('loc_elm_321', 'phone', NULL, 'good', 'voip', NULL),

-- Pine Road, Springfield - DSL area
('loc_pine_101', 'dsl_internet', 50, 'fair', 'dsl', NULL),
('loc_pine_101', 'tv', NULL, 'fair', 'satellite', NULL),
('loc_pine_101', 'mobile', NULL, 'fair', '4G', 3),

-- Maple Drive, Springfield - Mid-tier fiber
('loc_maple_555', 'fiber_internet', 1000, 'good', 'fiber', NULL),
('loc_maple_555', 'tv', NULL, 'good', 'fiber', NULL),
('loc_maple_555', 'mobile', NULL, 'good', '5G', 4),

-- Cherry Lane, Shelbyville - Cable area
('loc_cherry_777', 'cable_internet', 200, 'fair', 'cable', NULL),
('loc_cherry_777', 'tv', NULL, 'fair', 'cable', NULL),
('loc_cherry_777', 'mobile', NULL, 'poor', '4G', 2);

-- Customers (enhanced with location references)
INSERT INTO customers (id, name, account_status, credit_score, has_overdue_payments, street_number, street_name, city, postal_code) VALUES
('8452934', 'Jane Doe', 'active', 720, false, '456', 'Main Street', 'Springfield', '01101'),
('8452935', 'John Smith', 'active', 650, true, '123', 'Main Street', 'Springfield', '01101'),
('8452936', 'Alice Johnson', 'active', 780, false, '789', 'Oak Avenue', 'Springfield', '01102'),
('8452937', 'Bob Williams', 'suspended', 550, true, '321', 'Elm Street', 'Springfield', '01103'),
('8452938', 'Carol Brown', 'active', 695, false, '555', 'Maple Drive', 'Springfield', '01105'),
('8452939', 'David Lee', 'active', 640, false, '777', 'Cherry Lane', 'Shelbyville', '01201');

-- Keep original service coverage for backward compatibility
INSERT INTO service_coverage (street_name, city, service_type, max_speed_mbps) VALUES
-- Main Street, Springfield - Premium area with all services
('Main Street', 'Springfield', 'fiber_internet', 2000),
('Main Street', 'Springfield', 'wireless_broadband', 300),
('Main Street', 'Springfield', 'tv', NULL),
('Main Street', 'Springfield', 'mobile', NULL),
-- Oak Avenue, Springfield - Premium area with all services
('Oak Avenue', 'Springfield', 'fiber_internet', 2000),
('Oak Avenue', 'Springfield', 'wireless_broadband', 300),
('Oak Avenue', 'Springfield', 'tv', NULL),
('Oak Avenue', 'Springfield', 'mobile', NULL),
-- Elm Street, Springfield - Cable area
('Elm Street', 'Springfield', 'cable_internet', 400),
('Elm Street', 'Springfield', 'tv', NULL),
('Elm Street', 'Springfield', 'mobile', NULL),
-- Pine Road, Springfield - DSL area
('Pine Road', 'Springfield', 'dsl_internet', 50),
('Pine Road', 'Springfield', 'tv', NULL),
('Pine Road', 'Springfield', 'mobile', NULL),
-- Maple Drive, Springfield - Fiber area
('Maple Drive', 'Springfield', 'fiber_internet', 1000),
('Maple Drive', 'Springfield', 'tv', NULL),
-- Cherry Lane, Shelbyville - Cable area
('Cherry Lane', 'Shelbyville', 'cable_internet', 200),
('Cherry Lane', 'Shelbyville', 'tv', NULL),
('Cherry Lane', 'Shelbyville', 'mobile', NULL);

-- Create indexes for performance
CREATE INDEX idx_customers_status ON customers(account_status);
CREATE INDEX idx_coverage_location ON service_coverage(street_name, city);
CREATE INDEX idx_orders_customer ON orders(customer_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_order_status_history_order ON order_status_history(order_id);
CREATE INDEX idx_order_status_history_changed ON order_status_history(changed_at);

-- New indexes for enhanced tables
CREATE INDEX idx_geographic_locations_address ON geographic_locations(street_name, city);
CREATE INDEX idx_service_coverage_new_location ON service_coverage_new(location_id);
CREATE INDEX idx_service_coverage_new_type ON service_coverage_new(service_type);
CREATE INDEX idx_product_offerings_category ON product_offerings(category);
CREATE INDEX idx_product_offerings_active ON product_offerings(is_active);
CREATE INDEX idx_offering_service_links_offering ON offering_service_links(product_offering_id);
CREATE INDEX idx_offering_service_links_service ON offering_service_links(service_specification_id);
CREATE INDEX idx_catalog_integrity_type ON catalog_integrity(check_type);
CREATE INDEX idx_sync_operations_status ON sync_operations(status);

-- Insert some sample catalog integrity checks
INSERT INTO catalog_integrity (check_type, status, message, details) VALUES
('orphaned_offerings', 'passed', 'No product offerings without service specifications found', '{"checked_count": 12, "orphaned_count": 0}'),
('orphaned_services', 'passed', 'No service specifications without product offerings found', '{"checked_count": 20, "orphaned_count": 0}'),
('coverage_consistency', 'warning', 'Some locations have incomplete coverage data', '{"total_locations": 7, "incomplete_count": 1}'),
('pricing_validation', 'passed', 'All product offerings have valid pricing', '{"checked_count": 12, "invalid_count": 0}');

-- Insert a sample sync operation
INSERT INTO sync_operations (operation_type, status, records_processed, errors_count, details) VALUES
('full_catalog_sync', 'completed', 150, 0, '{"start_time": "2025-01-20T10:00:00Z", "end_time": "2025-01-20T10:05:23Z", "tables_synced": ["service_specifications", "product_offerings", "geographic_locations", "service_coverage_new"]}');
