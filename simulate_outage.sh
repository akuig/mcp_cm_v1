#!/bin/bash
# Simulate a fiber outage on Main Street for demo purposes

echo "Simulating fiber outage on Main Street..."
echo ""

# Call the fault manager API to create the outage
curl -X POST http://localhost:8081/api/simulate-outage \
  -H "Content-Type: application/json" \
  -s | jq .

echo ""
echo "✅ Fiber outage simulated on Main Street!"
echo ""
echo "You can now:"
echo "1. Check service status for Main Street"
echo "2. Create a trouble ticket for affected customers"
echo "3. Get remediation recommendations"
echo "4. Execute remediation actions"
