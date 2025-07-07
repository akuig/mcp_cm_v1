#!/bin/bash
# Fix database issues

echo "Fixing database issues..."
echo ""

# Fix the service type mismatch
echo "=== FIXING SERVICE TYPE MISMATCH ==="
docker exec -i telecom_postgres psql -U telecom_user -d telecom_catalog << 'EOF'
-- Update fiber coverage to use 'broadband' service type to match specifications
UPDATE service_coverage 
SET service_type = 'broadband' 
WHERE service_type = 'fiber';

-- Update cable coverage to use 'broadband' service type
UPDATE service_coverage 
SET service_type = 'broadband' 
WHERE service_type = 'cable';

-- Update dsl coverage to use 'broadband' service type
UPDATE service_coverage 
SET service_type = 'broadband' 
WHERE service_type = 'dsl';

-- Add missing cable100 service specification for Cherry Lane
INSERT INTO service_specifications (id, name, service_type, description) 
VALUES ('cable100', 'Cable 100 Mbps Plan', 'broadband', '100 Mbps cable internet service')
ON CONFLICT (id) DO NOTHING;

-- Show updated coverage
SELECT street_name, city, service_type, max_speed_mbps 
FROM service_coverage 
WHERE service_type = 'broadband'
ORDER BY street_name, city;

-- Show all service specifications for broadband
SELECT id, name, service_type, description
FROM service_specifications 
WHERE service_type = 'broadband'
ORDER BY id;
EOF

echo ""
echo "✅ Database fixed! Service types now match between coverage and specifications."
