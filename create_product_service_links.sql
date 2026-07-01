-- SQL Script to create product_service_links table
-- This table links product offerings to their underlying service specifications
-- Database: telecom_catalog
-- User: telecom_user

\c telecom_catalog;

-- Create the product_service_links table
-- This is the table name expected by the MCP catalog manager code
CREATE TABLE IF NOT EXISTS product_service_links (
    id SERIAL PRIMARY KEY,
    product_offering_id VARCHAR(50) NOT NULL,
    service_specification_id VARCHAR(50) NOT NULL,
    is_primary BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_product_offering 
        FOREIGN KEY (product_offering_id) 
        REFERENCES product_offerings(id) 
        ON DELETE CASCADE,
    CONSTRAINT fk_service_specification 
        FOREIGN KEY (service_specification_id) 
        REFERENCES service_specifications(id) 
        ON DELETE CASCADE,
    CONSTRAINT unique_product_service 
        UNIQUE(product_offering_id, service_specification_id)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_psl_product_offering 
    ON product_service_links(product_offering_id);
    
CREATE INDEX IF NOT EXISTS idx_psl_service_specification 
    ON product_service_links(service_specification_id);
    
CREATE INDEX IF NOT EXISTS idx_psl_primary 
    ON product_service_links(is_primary);

-- Insert product-to-service mappings
-- These link the 14 product offerings to their underlying 22 service specifications

-- ============================================
-- INTERNET ONLY PACKAGES
-- ============================================

-- TeleCo Fiber 500 (pkg_fiber_500)
INSERT INTO product_service_links (product_offering_id, service_specification_id, is_primary) 
VALUES ('pkg_fiber_500', 'fiber_500', true);

-- TeleCo Fiber Gig (pkg_fiber_1000)
INSERT INTO product_service_links (product_offering_id, service_specification_id, is_primary) 
VALUES ('pkg_fiber_1000', 'fiber_1000', true);

-- TeleCo Fiber Pro (pkg_fiber_2000)
INSERT INTO product_service_links (product_offering_id, service_specification_id, is_primary) 
VALUES ('pkg_fiber_2000', 'fiber_2000', true);

-- TeleCo Cable Max (pkg_cable_400)
INSERT INTO product_service_links (product_offering_id, service_specification_id, is_primary) 
VALUES ('pkg_cable_400', 'cable_400', true);

-- TeleCo 5G Home (pkg_wireless_300)
INSERT INTO product_service_links (product_offering_id, service_specification_id, is_primary) 
VALUES ('pkg_wireless_300', 'wireless_300', true);

-- ============================================
-- TV ONLY PACKAGES
-- ============================================

-- TeleCo Basic TV (pkg_tv_basic)
INSERT INTO product_service_links (product_offering_id, service_specification_id, is_primary) 
VALUES ('pkg_tv_basic', 'tv_basic', true);

-- TeleCo Premium TV (pkg_tv_premium)
INSERT INTO product_service_links (product_offering_id, service_specification_id, is_primary) 
VALUES ('pkg_tv_premium', 'tv_premium', true);

-- TeleCo Stream TV (pkg_tv_streaming)
INSERT INTO product_service_links (product_offering_id, service_specification_id, is_primary) 
VALUES ('pkg_tv_streaming', 'tv_streaming', true);

-- ============================================
-- MOBILE ONLY PACKAGES
-- ============================================

-- TeleCo Family Mobile (pkg_mobile_family)
INSERT INTO product_service_links (product_offering_id, service_specification_id, is_primary) 
VALUES ('pkg_mobile_family', 'mobile_unlimited', true);

-- TeleCo Unlimited Mobile (pkg_mobile_unlimited)
INSERT INTO product_service_links (product_offering_id, service_specification_id, is_primary) 
VALUES ('pkg_mobile_unlimited', 'mobile_unlimited', true);

-- ============================================
-- BUNDLE PACKAGES
-- ============================================

-- TeleCo Triple Play (pkg_triple_play)
-- Internet + TV + Phone bundle
INSERT INTO product_service_links (product_offering_id, service_specification_id, is_primary) VALUES
('pkg_triple_play', 'fiber_1000', true),  -- Primary: 1 Gbps Internet
('pkg_triple_play', 'tv_premium', false), -- Premium TV
('pkg_triple_play', 'phone_basic', false); -- Basic Phone

-- TeleCo Internet + TV (pkg_double_play_it)
-- High-speed internet and premium TV
INSERT INTO product_service_links (product_offering_id, service_specification_id, is_primary) VALUES
('pkg_double_play_it', 'fiber_500', true),  -- Primary: 500 Mbps Internet
('pkg_double_play_it', 'tv_premium', false); -- Premium TV

-- TeleCo Smart Home (pkg_smart_home)
-- Internet + TV + Security bundle
INSERT INTO product_service_links (product_offering_id, service_specification_id, is_primary) VALUES
('pkg_smart_home', 'fiber_1000', true),        -- Primary: 1 Gbps Internet
('pkg_smart_home', 'tv_basic', false),         -- Basic TV
('pkg_smart_home', 'security_premium', false); -- Premium Security

-- TeleCo Everything (pkg_everything)
-- Complete home connectivity solution
INSERT INTO product_service_links (product_offering_id, service_specification_id, is_primary) VALUES
('pkg_everything', 'fiber_2000', true),           -- Primary: 2 Gbps Internet
('pkg_everything', 'tv_ultimate', false),         -- Ultimate TV
('pkg_everything', 'phone_international', false), -- International Phone
('pkg_everything', 'mobile_unlimited', false),    -- Unlimited Mobile
('pkg_everything', 'security_premium', false);    -- Premium Security

-- ============================================
-- VERIFICATION QUERIES
-- ============================================

-- Count total links
SELECT COUNT(*) as total_links FROM product_service_links;

-- Count products with services
SELECT COUNT(DISTINCT product_offering_id) as products_with_services 
FROM product_service_links;

-- Count services linked to products
SELECT COUNT(DISTINCT service_specification_id) as services_in_use 
FROM product_service_links;

-- Show all product-to-service mappings
SELECT 
    po.name as product_name,
    po.category,
    ss.name as service_name,
    ss.service_type,
    psl.is_primary
FROM product_service_links psl
JOIN product_offerings po ON psl.product_offering_id = po.id
JOIN service_specifications ss ON psl.service_specification_id = ss.id
ORDER BY po.category, po.name, psl.is_primary DESC;

-- Find products without services (should be empty)
SELECT po.id, po.name, po.category
FROM product_offerings po
LEFT JOIN product_service_links psl ON po.id = psl.product_offering_id
WHERE psl.id IS NULL;

-- Find services not linked to any product
SELECT ss.id, ss.name, ss.service_type
FROM service_specifications ss
LEFT JOIN product_service_links psl ON ss.id = psl.service_specification_id
WHERE psl.id IS NULL
ORDER BY ss.service_type, ss.name;

-- Show bundle composition
SELECT 
    po.name as bundle_name,
    COUNT(*) as service_count,
    STRING_AGG(ss.name || ' (' || CASE WHEN psl.is_primary THEN 'Primary' ELSE 'Secondary' END || ')', ', ' ORDER BY psl.is_primary DESC) as services
FROM product_offerings po
JOIN product_service_links psl ON po.id = psl.product_offering_id
JOIN service_specifications ss ON ss.id = psl.service_specification_id
WHERE po.category = 'bundle'
GROUP BY po.id, po.name
ORDER BY po.name;

COMMIT;
