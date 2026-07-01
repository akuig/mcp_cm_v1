#!/bin/bash
# Quick script to fix Server 2 critical issue only

echo "Fixing Server 2 (Fanore) critical issue..."
docker cp fix_server2_critical.sql telecom_postgres:/tmp/ && \
docker exec telecom_postgres psql -U telecom_user -d telecom_catalog -f /tmp/fix_server2_critical.sql && \
docker exec telecom_postgres rm /tmp/fix_server2_critical.sql

if [ $? -eq 0 ]; then
    echo "✅ Server 2 fixed - Business Fiber Pro is now operational"
else
    echo "❌ Fix failed"
fi
