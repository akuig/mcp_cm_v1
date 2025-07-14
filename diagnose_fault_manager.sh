#!/bin/bash
# Diagnose fault manager issues

echo "🔍 Diagnosing Fault Manager Issues..."
echo "===================================="
echo ""

# Check container status
echo "1. Container Status:"
docker-compose -f docker-compose-with-fault.yml ps

echo -e "\n2. Fault Manager Logs:"
docker-compose -f docker-compose-with-fault.yml logs --tail=50 fault-manager

echo -e "\n3. Checking if fault manager is responding:"
curl -v http://localhost:8081/docs 2>&1 | head -20

echo -e "\n4. Checking container health status:"
docker inspect fault_manager --format='{{json .State.Health}}' | python3 -m json.tool

echo -e "\n5. Testing fault manager directly:"
docker-compose -f docker-compose-with-fault.yml exec fault-manager curl -f http://localhost:8081/docs || echo "Failed to connect inside container"

echo -e "\n6. Check if port 8081 is in use:"
lsof -i :8081 || echo "Port 8081 not in use"
