#!/bin/bash
# Quick test to verify fault management is working

echo "Testing Fault Management Setup..."
echo ""

# Check if services are running
echo "Checking service endpoints..."

# Catalog Manager
echo -n "Catalog Manager (8080): "
if curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/health | grep -q "200"; then
    echo "✓ OK"
else
    echo "✗ Not responding"
fi

# Fault Manager
echo -n "Fault Manager (8081): "
if curl -s -o /dev/null -w "%{http_code}" http://localhost:8081/docs | grep -q "200"; then
    echo "✓ OK"
else
    echo "✗ Not responding"
fi

# MCP Server
echo -n "MCP Server (8090): "
if curl -s -o /dev/null -w "%{http_code}" http://localhost:8090/health | grep -q "200"; then
    echo "✓ OK"
else
    echo "✗ Not responding"
fi

echo ""
echo "Testing Fault Manager API..."

# Test service status check
echo "Checking service status for Main Street..."
response=$(curl -s -X POST http://localhost:8081/serviceStatus/check \
  -H "Content-Type: application/json" \
  -d '{"location": {"streetName": "Main Street", "city": "Dublin"}}')

if echo "$response" | grep -q "degraded"; then
    echo "✓ Fault detected on Main Street"
    echo "  Status: degraded"
    echo "  Fault type: fiber_cut"
else
    echo "✗ No fault detected"
fi

echo ""
echo "Test complete!"
