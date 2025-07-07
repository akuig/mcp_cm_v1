#!/bin/bash
# Comprehensive database fix to align service specifications and coverage

echo "Fixing service specifications and coverage alignment..."
echo ""

# Reset and fix the database
docker exec -i telecom_postgres psql -U telecom_user -d telecom_catalog << 'EOF'
-- First, clear existing data to start fresh
TRUNCATE service_specifications CASCADE;
TRUNCATE service_coverage CASCADE;

-- Create a consistent set of service specifications
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

-- Now create service coverage that matches these specifications
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

-- Display the aligned data
\echo ''
\echo '=== SERVICE SPECIFICATIONS BY TYPE ==='
SELECT service_type, COUNT(*) as count, STRING_AGG(id, ', ' ORDER BY id) as service_ids
FROM service_specifications
GROUP BY service_type
ORDER BY service_type;

\echo ''
\echo '=== SERVICE COVERAGE BY LOCATION ==='
SELECT street_name, city, 
       STRING_AGG(DISTINCT service_type, ', ' ORDER BY service_type) as available_services
FROM service_coverage
GROUP BY street_name, city
ORDER BY city, street_name;

\echo ''
\echo '=== DETAILED COVERAGE FOR MAIN STREET ==='
SELECT sc.service_type, sc.max_speed_mbps,
       STRING_AGG(ss.id || ' (' || ss.name || ')', ', ' ORDER BY ss.id) as available_plans
FROM service_coverage sc
LEFT JOIN service_specifications ss ON sc.service_type = ss.service_type
WHERE sc.street_name = 'Main Street' AND sc.city = 'Springfield'
GROUP BY sc.service_type, sc.max_speed_mbps
ORDER BY sc.service_type;

EOF

echo ""
echo "✅ Database fixed! Service specifications and coverage are now properly aligned."
echo ""
echo "Service Types Available:"
echo "- fiber_internet: Fiber 500/1000 Mbps"
echo "- cable_internet: Cable 100/200 Mbps"
echo "- dsl_internet: DSL 50 Mbps"
echo "- wireless_broadband: Wireless 50/150 Mbps"
echo "- tv: Basic/Premium/Ultimate packages"
echo "- mobile: 5GB/25GB/Unlimited plans"
