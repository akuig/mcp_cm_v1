-- Database Migration Script for Telepath Catalog Manager
-- Version: 1.0
-- Description: Initial schema for TMF Forum APIs

-- Drop existing tables if they exist (for clean deployment)
DROP TABLE IF EXISTS service_coverage CASCADE;
DROP TABLE IF EXISTS offering_service_mappings CASCADE;
DROP TABLE IF EXISTS service_spec_characteristics CASCADE;
DROP TABLE IF EXISTS service_specifications CASCADE;
DROP TABLE IF EXISTS product_offerings CASCADE;
DROP TABLE IF EXISTS geographic_locations CASCADE;
DROP TABLE IF EXISTS customers CASCADE;

-- Service Specifications (TMF633)
CREATE TABLE service_specifications (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(100),
    service_type VARCHAR(100),
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Service Specification Characteristics
CREATE TABLE service_spec_characteristics (
    id VARCHAR(50) PRIMARY KEY,
    service_spec_id VARCHAR(50),
    name VARCHAR(255) NOT NULL,
    value_type VARCHAR(50),
    default_value TEXT,
    is_configurable BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (service_spec_id) REFERENCES service_specifications(id) ON DELETE CASCADE
);

-- Product Offerings (TMF620)
CREATE TABLE product_offerings (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(100),
    is_bundle BOOLEAN DEFAULT false,
    status VARCHAR(50) DEFAULT 'active',
    price_amount DECIMAL(10,2),
    price_currency VARCHAR(10) DEFAULT 'USD',
    price_period VARCHAR(50) DEFAULT 'monthly',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Geographic Locations (TMF673)
CREATE TABLE geographic_locations (
    id VARCHAR(50) PRIMARY KEY,
    street_name VARCHAR(255),
    street_number VARCHAR(50),
    city VARCHAR(100),
    postal_code VARCHAR(20),
    state VARCHAR(100),
    country VARCHAR(100) DEFAULT 'US',
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Service Coverage (Mapping table)
CREATE TABLE service_coverage (
    id VARCHAR(50) PRIMARY KEY,
    service_spec_id VARCHAR(50),
    location_id VARCHAR(50),
    coverage_type VARCHAR(50) DEFAULT 'full', -- full, partial, planned
    installation_type VARCHAR(50) DEFAULT 'standard', -- standard, complex, not_feasible
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (service_spec_id) REFERENCES service_specifications(id) ON DELETE CASCADE,
    FOREIGN KEY (location_id) REFERENCES geographic_locations(id) ON DELETE CASCADE,
    UNIQUE KEY unique_coverage (service_spec_id, location_id)
);

-- Product Offering to Service Specification Mapping
CREATE TABLE offering_service_mappings (
    id VARCHAR(50) PRIMARY KEY,
    product_offering_id VARCHAR(50),
    service_spec_id VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_offering_id) REFERENCES product_offerings(id) ON DELETE CASCADE,
    FOREIGN KEY (service_spec_id) REFERENCES service_specifications(id) ON DELETE CASCADE,
    UNIQUE KEY unique_mapping (product_offering_id, service_spec_id)
);

-- Customers (for TMF629)
CREATE TABLE customers (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    phone VARCHAR(50),
    account_status VARCHAR(50) DEFAULT 'active',
    credit_score INTEGER,
    has_overdue_payments BOOLEAN DEFAULT false,
    street_name VARCHAR(255),
    street_number VARCHAR(50),
    city VARCHAR(100),
    postal_code VARCHAR(20),
    state VARCHAR(100) DEFAULT 'IL',
    country VARCHAR(100) DEFAULT 'US',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX idx_service_specs_category ON service_specifications(category);
CREATE INDEX idx_service_specs_type ON service_specifications(service_type);
CREATE INDEX idx_product_offerings_category ON product_offerings(category);
CREATE INDEX idx_geographic_locations_city ON geographic_locations(city);
CREATE INDEX idx_service_coverage_spec ON service_coverage(service_spec_id);
CREATE INDEX idx_service_coverage_location ON service_coverage(location_id);
CREATE INDEX idx_customers_city ON customers(city);

-- Views for easier querying
CREATE VIEW service_offerings_view AS
SELECT 
    po.id as offering_id,
    po.name as offering_name,
    po.description as offering_description,
    po.category,
    po.is_bundle,
    po.price_amount,
    po.price_currency,
    po.price_period,
    po.status,
    ss.id as service_spec_id,
    ss.name as service_spec_name,
    ss.service_type
FROM product_offerings po
LEFT JOIN offering_service_mappings osm ON po.id = osm.product_offering_id
LEFT JOIN service_specifications ss ON osm.service_spec_id = ss.id
WHERE po.status = 'active' AND (ss.status = 'active' OR ss.status IS NULL);

CREATE VIEW geographic_coverage_view AS
SELECT 
    gl.id as location_id,
    gl.street_name,
    gl.street_number,
    gl.city,
    gl.postal_code,
    gl.state,
    ss.id as service_spec_id,
    ss.name as service_name,
    ss.service_type,
    sc.coverage_type,
    sc.installation_type
FROM geographic_locations gl
LEFT JOIN service_coverage sc ON gl.id = sc.location_id
LEFT JOIN service_specifications ss ON sc.service_spec_id = ss.id
WHERE ss.status = 'active' OR ss.status IS NULL;

-- Triggers for updated_at timestamps
DELIMITER //

CREATE TRIGGER service_specs_updated_at
    BEFORE UPDATE ON service_specifications
    FOR EACH ROW
BEGIN
    SET NEW.updated_at = CURRENT_TIMESTAMP;
END//

CREATE TRIGGER product_offerings_updated_at
    BEFORE UPDATE ON product_offerings
    FOR EACH ROW
BEGIN
    SET NEW.updated_at = CURRENT_TIMESTAMP;
END//

CREATE TRIGGER customers_updated_at
    BEFORE UPDATE ON customers
    FOR EACH ROW
BEGIN
    SET NEW.updated_at = CURRENT_TIMESTAMP;
END//

DELIMITER ;

-- Grant permissions (adjust as needed for your environment)
-- GRANT ALL PRIVILEGES ON *.* TO 'catalog_user'@'%';
-- FLUSH PRIVILEGES;