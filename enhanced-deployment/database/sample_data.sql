-- Sample Data Insertion Script for Telepath Catalog Manager
-- Version: 1.0
-- Description: Demo data for testing TMF Forum APIs

-- Clear existing data
DELETE FROM service_coverage;
DELETE FROM offering_service_mappings;
DELETE FROM service_spec_characteristics;
DELETE FROM service_specifications;
DELETE FROM product_offerings;
DELETE FROM geographic_locations;
DELETE FROM customers;

-- Insert Service Specifications (TMF633)
INSERT INTO service_specifications (id, name, description, category, service_type, status) VALUES
('FIBER_1GB', 'Fiber Internet 1 Gbps', 'High-speed fiber internet service with 1 Gbps download/upload', 'connectivity', 'broadband', 'active'),
('FIBER_500MB', 'Fiber Internet 500 Mbps', 'High-speed fiber internet service with 500 Mbps download/upload', 'connectivity', 'broadband', 'active'),
('FIBER_100MB', 'Fiber Internet 100 Mbps', 'Standard fiber internet service with 100 Mbps download/upload', 'connectivity', 'broadband', 'active'),
('DSL_25MB', 'DSL Internet 25 Mbps', 'DSL internet service with 25 Mbps download', 'connectivity', 'broadband', 'active'),
('DSL_10MB', 'DSL Internet 10 Mbps', 'Basic DSL internet service with 10 Mbps download', 'connectivity', 'broadband', 'active'),
('VOICE_BASIC', 'Basic Voice Service', 'Standard residential voice service with unlimited local calling', 'voice', 'telephony', 'active'),
('VOICE_PREMIUM', 'Premium Voice Service', 'Premium voice service with unlimited long distance and features', 'voice', 'telephony', 'active'),
('TV_BASIC', 'Basic TV Package', 'Basic cable TV package with 50+ channels', 'entertainment', 'television', 'active'),
('TV_PREMIUM', 'Premium TV Package', 'Premium cable TV package with 200+ channels and premium networks', 'entertainment', 'television', 'active'),
('TV_SPORTS', 'Sports TV Package', 'Sports-focused TV package with all major sports networks', 'entertainment', 'television', 'active');

-- Insert Service Specification Characteristics
INSERT INTO service_spec_characteristics (id, service_spec_id, name, value_type, default_value, is_configurable) VALUES
-- Fiber 1GB characteristics
('CHAR_F1G_BW_DOWN', 'FIBER_1GB', 'download_bandwidth', 'string', '1000 Mbps', false),
('CHAR_F1G_BW_UP', 'FIBER_1GB', 'upload_bandwidth', 'string', '1000 Mbps', false),
('CHAR_F1G_TECH', 'FIBER_1GB', 'technology', 'string', 'GPON', false),
('CHAR_F1G_SLA', 'FIBER_1GB', 'sla_uptime', 'string', '99.9%', false),

-- Fiber 500MB characteristics  
('CHAR_F500_BW_DOWN', 'FIBER_500MB', 'download_bandwidth', 'string', '500 Mbps', false),
('CHAR_F500_BW_UP', 'FIBER_500MB', 'upload_bandwidth', 'string', '500 Mbps', false),
('CHAR_F500_TECH', 'FIBER_500MB', 'technology', 'string', 'GPON', false),

-- DSL characteristics
('CHAR_DSL25_BW_DOWN', 'DSL_25MB', 'download_bandwidth', 'string', '25 Mbps', false),
('CHAR_DSL25_BW_UP', 'DSL_25MB', 'upload_bandwidth', 'string', '3 Mbps', false),
('CHAR_DSL25_TECH', 'DSL_25MB', 'technology', 'string', 'VDSL2', false),

-- Voice characteristics
('CHAR_VOICE_BASIC_FEAT', 'VOICE_BASIC', 'features', 'array', 'caller_id,call_waiting', true),
('CHAR_VOICE_PREM_FEAT', 'VOICE_PREMIUM', 'features', 'array', 'caller_id,call_waiting,voicemail,call_forwarding,3way_calling', true),

-- TV characteristics
('CHAR_TV_BASIC_CHAN', 'TV_BASIC', 'channel_count', 'number', '50', false),
('CHAR_TV_PREM_CHAN', 'TV_PREMIUM', 'channel_count', 'number', '200', false),
('CHAR_TV_SPORTS_CHAN', 'TV_SPORTS', 'channel_count', 'number', '150', false);

-- Insert Product Offerings (TMF620)
INSERT INTO product_offerings (id, name, description, category, is_bundle, status, price_amount, price_currency, price_period) VALUES
-- Individual Services
('FIBER_HOME_1GB', 'Home Fiber 1GB Package', 'Residential fiber internet with 1 Gbps speed', 'residential', false, 'active', 79.99, 'USD', 'monthly'),
('FIBER_HOME_500MB', 'Home Fiber 500MB Package', 'Residential fiber internet with 500 Mbps speed', 'residential', false, 'active', 59.99, 'USD', 'monthly'),
('FIBER_HOME_100MB', 'Home Fiber 100MB Package', 'Residential fiber internet with 100 Mbps speed', 'residential', false, 'active', 39.99, 'USD', 'monthly'),
('DSL_HOME_25MB', 'Home DSL 25MB Package', 'Residential DSL internet with 25 Mbps speed', 'residential', false, 'active', 29.99, 'USD', 'monthly'),
('DSL_HOME_10MB', 'Home DSL 10MB Package', 'Basic residential DSL internet with 10 Mbps speed', 'residential', false, 'active', 19.99, 'USD', 'monthly'),
('VOICE_HOME_BASIC', 'Home Voice Basic', 'Basic residential voice service', 'residential', false, 'active', 19.99, 'USD', 'monthly'),
('VOICE_HOME_PREMIUM', 'Home Voice Premium', 'Premium residential voice service with features', 'residential', false, 'active', 29.99, 'USD', 'monthly'),
('TV_HOME_BASIC', 'Home TV Basic', 'Basic cable TV package for home', 'residential', false, 'active', 49.99, 'USD', 'monthly'),
('TV_HOME_PREMIUM', 'Home TV Premium', 'Premium cable TV package for home', 'residential', false, 'active', 89.99, 'USD', 'monthly'),

-- Bundle Packages
('DOUBLE_PLAY_FIBER', 'Double Play Fiber + Voice', 'Fiber internet 500MB + Premium Voice bundle', 'residential', true, 'active', 79.99, 'USD', 'monthly'),
('TRIPLE_PLAY_FIBER', 'Triple Play Fiber + Voice + TV', 'Fiber internet 1GB + Premium Voice + Premium TV bundle', 'residential', true, 'active', 129.99, 'USD', 'monthly'),
('DOUBLE_PLAY_DSL', 'Double Play DSL + Voice', 'DSL internet 25MB + Basic Voice bundle', 'residential', true, 'active', 44.99, 'USD', 'monthly'),

-- Business Offerings
('FIBER_BIZ_1GB', 'Business Fiber 1GB', 'Business-grade fiber internet with SLA', 'business', false, 'active', 149.99, 'USD', 'monthly'),
('FIBER_BIZ_500MB', 'Business Fiber 500MB', 'Business-grade fiber internet', 'business', false, 'active', 99.99, 'USD', 'monthly');

-- Insert Geographic Locations (TMF673)
INSERT INTO geographic_locations (id, street_name, street_number, city, postal_code, state, country, latitude, longitude) VALUES
-- Springfield locations
('LOC_SPR_MAIN_456', 'Main Street', '456', 'Springfield', '01101', 'IL', 'US', 39.7817, -89.6501),
('LOC_SPR_MAIN_123', 'Main Street', '123', 'Springfield', '01101', 'IL', 'US', 39.7820, -89.6498),
('LOC_SPR_MAIN_789', 'Main Street', '789', 'Springfield', '01101', 'IL', 'US', 39.7814, -89.6504),
('LOC_SPR_ELM_100', 'Elm Street', '100', 'Springfield', '01102', 'IL', 'US', 39.7825, -89.6510),
('LOC_SPR_ELM_200', 'Elm Street', '200', 'Springfield', '01102', 'IL', 'US', 39.7830, -89.6515),
('LOC_SPR_OAK_50', 'Oak Avenue', '50', 'Springfield', '01103', 'IL', 'US', 39.7800, -89.6520),

-- Shelbyville locations (limited coverage)
('LOC_SHE_FIRST_100', 'First Street', '100', 'Shelbyville', '62565', 'IL', 'US', 39.4062, -88.7901),
('LOC_SHE_FIRST_200', 'First Street', '200', 'Shelbyville', '62565', 'IL', 'US', 39.4065, -88.7905),
('LOC_SHE_SECOND_150', 'Second Street', '150', 'Shelbyville', '62565', 'IL', 'US', 39.4070, -88.7910),

-- Capital City locations (full coverage)
('LOC_CAP_STATE_1000', 'State Street', '1000', 'Capital City', '62701', 'IL', 'US', 39.7391, -89.2661),
('LOC_CAP_STATE_1200', 'State Street', '1200', 'Capital City', '62701', 'IL', 'US', 39.7395, -89.2665),
('LOC_CAP_CAPITOL_500', 'Capitol Avenue', '500', 'Capital City', '62702', 'IL', 'US', 39.7400, -89.2670),

-- Ogdenville locations (DSL only)
('LOC_OGD_RAIL_300', 'Railroad Avenue', '300', 'Ogdenville', '61859', 'IL', 'US', 40.1234, -88.1234),
('LOC_OGD_RAIL_400', 'Railroad Avenue', '400', 'Ogdenville', '61859', 'IL', 'US', 40.1238, -88.1230);

-- Insert Service Coverage mappings
INSERT INTO service_coverage (id, service_spec_id, location_id, coverage_type, installation_type) VALUES
-- Springfield - Full fiber coverage
('COV_SPR_MAIN_456_F1G', 'FIBER_1GB', 'LOC_SPR_MAIN_456', 'full', 'standard'),
('COV_SPR_MAIN_456_F500', 'FIBER_500MB', 'LOC_SPR_MAIN_456', 'full', 'standard'),
('COV_SPR_MAIN_456_F100', 'FIBER_100MB', 'LOC_SPR_MAIN_456', 'full', 'standard'),
('COV_SPR_MAIN_456_VOI_B', 'VOICE_BASIC', 'LOC_SPR_MAIN_456', 'full', 'standard'),
('COV_SPR_MAIN_456_VOI_P', 'VOICE_PREMIUM', 'LOC_SPR_MAIN_456', 'full', 'standard'),
('COV_SPR_MAIN_456_TV_B', 'TV_BASIC', 'LOC_SPR_MAIN_456', 'full', 'standard'),
('COV_SPR_MAIN_456_TV_P', 'TV_PREMIUM', 'LOC_SPR_MAIN_456', 'full', 'standard'),

-- More Springfield locations
('COV_SPR_MAIN_123_F1G', 'FIBER_1GB', 'LOC_SPR_MAIN_123', 'full', 'standard'),
('COV_SPR_MAIN_123_F500', 'FIBER_500MB', 'LOC_SPR_MAIN_123', 'full', 'standard'),
('COV_SPR_ELM_100_F500', 'FIBER_500MB', 'LOC_SPR_ELM_100', 'full', 'standard'),
('COV_SPR_ELM_100_F100', 'FIBER_100MB', 'LOC_SPR_ELM_100', 'full', 'standard'),

-- Shelbyville - DSL only
('COV_SHE_FIRST_100_DSL25', 'DSL_25MB', 'LOC_SHE_FIRST_100', 'full', 'standard'),
('COV_SHE_FIRST_100_DSL10', 'DSL_10MB', 'LOC_SHE_FIRST_100', 'full', 'standard'),
('COV_SHE_FIRST_100_VOI_B', 'VOICE_BASIC', 'LOC_SHE_FIRST_100', 'full', 'standard'),
('COV_SHE_FIRST_200_DSL25', 'DSL_25MB', 'LOC_SHE_FIRST_200', 'full', 'standard'),

-- Capital City - Full coverage
('COV_CAP_STATE_1000_F1G', 'FIBER_1GB', 'LOC_CAP_STATE_1000', 'full', 'standard'),
('COV_CAP_STATE_1000_F500', 'FIBER_500MB', 'LOC_CAP_STATE_1000', 'full', 'standard'),
('COV_CAP_STATE_1000_TV_P', 'TV_PREMIUM', 'LOC_CAP_STATE_1000', 'full', 'standard'),

-- Ogdenville - DSL only
('COV_OGD_RAIL_300_DSL10', 'DSL_10MB', 'LOC_OGD_RAIL_300', 'full', 'standard'),
('COV_OGD_RAIL_300_VOI_B', 'VOICE_BASIC', 'LOC_OGD_RAIL_300', 'full', 'standard');

-- Insert Product Offering to Service Specification mappings
INSERT INTO offering_service_mappings (id, product_offering_id, service_spec_id) VALUES
-- Individual service mappings
('MAP_F1G_HOME', 'FIBER_HOME_1GB', 'FIBER_1GB'),
('MAP_F500_HOME', 'FIBER_HOME_500MB', 'FIBER_500MB'),
('MAP_F100_HOME', 'FIBER_HOME_100MB', 'FIBER_100MB'),
('MAP_DSL25_HOME', 'DSL_HOME_25MB', 'DSL_25MB'),
('MAP_DSL10_HOME', 'DSL_HOME_10MB', 'DSL_10MB'),
('MAP_VOICE_B_HOME', 'VOICE_HOME_BASIC', 'VOICE_BASIC'),
('MAP_VOICE_P_HOME', 'VOICE_HOME_PREMIUM', 'VOICE_PREMIUM'),
('MAP_TV_B_HOME', 'TV_HOME_BASIC', 'TV_BASIC'),
('MAP_TV_P_HOME', 'TV_HOME_PREMIUM', 'TV_PREMIUM'),

-- Bundle mappings
('MAP_DBL_FIBER_INT', 'DOUBLE_PLAY_FIBER', 'FIBER_500MB'),
('MAP_DBL_FIBER_VOI', 'DOUBLE_PLAY_FIBER', 'VOICE_PREMIUM'),
('MAP_TRP_FIBER_INT', 'TRIPLE_PLAY_FIBER', 'FIBER_1GB'),
('MAP_TRP_FIBER_VOI', 'TRIPLE_PLAY_FIBER', 'VOICE_PREMIUM'),
('MAP_TRP_FIBER_TV', 'TRIPLE_PLAY_FIBER', 'TV_PREMIUM'),
('MAP_DBL_DSL_INT', 'DOUBLE_PLAY_DSL', 'DSL_25MB'),
('MAP_DBL_DSL_VOI', 'DOUBLE_PLAY_DSL', 'VOICE_BASIC'),

-- Business mappings
('MAP_BIZ_F1G', 'FIBER_BIZ_1GB', 'FIBER_1GB'),
('MAP_BIZ_F500', 'FIBER_BIZ_500MB', 'FIBER_500MB');

-- Insert Customer data (including customer 8452934)
INSERT INTO customers (id, name, email, phone, account_status, credit_score, has_overdue_payments, street_name, street_number, city, postal_code, state, country) VALUES
('8452934', 'Jane Doe', 'jane.doe@email.com', '555-0123', 'active', 720, false, 'Main Street', '456', 'Springfield', '01101', 'IL', 'US'),
('1234567', 'John Smith', 'john.smith@email.com', '555-0124', 'active', 680, false, 'Elm Street', '100', 'Springfield', '01102', 'IL', 'US'),
('2345678', 'Mary Johnson', 'mary.johnson@email.com', '555-0125', 'active', 750, false, 'First Street', '100', 'Shelbyville', '62565', 'IL', 'US'),
('3456789', 'Bob Wilson', 'bob.wilson@email.com', '555-0126', 'suspended', 580, true, 'Railroad Avenue', '300', 'Ogdenville', '61859', 'IL', 'US'),
('4567890', 'Alice Brown', 'alice.brown@email.com', '555-0127', 'active', 790, false, 'State Street', '1000', 'Capital City', '62701', 'IL', 'US'),
('5678901', 'Charlie Davis', 'charlie.davis@email.com', '555-0128', 'active', 650, false, 'Oak Avenue', '50', 'Springfield', '01103', 'IL', 'US'),
('6789012', 'Diana Miller', 'diana.miller@email.com', '555-0129', 'inactive', 700, false, 'Second Street', '150', 'Shelbyville', '62565', 'IL', 'US'),
('7890123', 'Frank Garcia', 'frank.garcia@email.com', '555-0130', 'active', 720, false, 'Capitol Avenue', '500', 'Capital City', '62702', 'IL', 'US');

-- Verify data insertion
SELECT 'Service Specifications' as table_name, COUNT(*) as record_count FROM service_specifications
UNION ALL
SELECT 'Product Offerings', COUNT(*) FROM product_offerings
UNION ALL  
SELECT 'Geographic Locations', COUNT(*) FROM geographic_locations
UNION ALL
SELECT 'Service Coverage', COUNT(*) FROM service_coverage
UNION ALL
SELECT 'Offering-Service Mappings', COUNT(*) FROM offering_service_mappings
UNION ALL
SELECT 'Customers', COUNT(*) FROM customers;