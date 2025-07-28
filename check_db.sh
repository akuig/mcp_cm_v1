#!/bin/bash
# Check database contents

echo "Checking database contents..."
echo ""

# Check service specifications
echo "=== SERVICE SPECIFICATIONS ==="
docker exec -i telecom_postgres psql -U telecom_user -d telecom_catalog << 'EOF'
SELECT id, name, service_type FROM service_specifications ORDER BY service_type, id;
EOF

echo ""
echo "=== SERVICE COVERAGE ==="
docker exec -i telecom_postgres psql -U telecom_user -d telecom_catalog << 'EOF'
SELECT street_name, city, service_type, max_speed_mbps 
FROM service_coverage 
WHERE street_name IN ('Main Street', 'Cherry Lane')
ORDER BY street_name, city, service_type;
EOF

echo ""
echo "=== CHECKING FIBER SERVICES ==="
docker exec -i telecom_postgres psql -U telecom_user -d telecom_catalog << 'EOF'
-- Check if fiber services exist in specifications
SELECT * FROM service_specifications WHERE id IN ('fiber500', 'fiber1000');

-- Check fiber coverage
SELECT * FROM service_coverage WHERE service_type = 'fiber';
EOF

echo ""
echo "=== CHECKING BROADBAND VS FIBER MISMATCH ==="
docker exec -i telecom_postgres psql -U telecom_user -d telecom_catalog << 'EOF'
-- Service specs with type 'broadband'
SELECT id, service_type FROM service_specifications WHERE service_type = 'broadband';

-- Coverage with type 'fiber'
SELECT DISTINCT service_type FROM service_coverage WHERE service_type IN ('fiber', 'broadband');
EOF
