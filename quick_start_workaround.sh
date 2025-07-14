#!/bin/bash
# Quick workaround - start everything without waiting for health checks

echo "🚀 Quick Start - Fault Management Demo"
echo "======================================"
echo ""
echo "Starting all services without health check dependencies..."

# Stop everything first
docker-compose -f docker-compose-with-fault.yml down

# Start all services at once
docker-compose -f docker-compose-with-fault.yml up -d

echo "⏳ Waiting 30 seconds for all services to initialize..."
sleep 30

# Check what's running
echo ""
echo "📊 Service Status:"
docker-compose -f docker-compose-with-fault.yml ps

echo ""
echo "🔍 Quick Health Check:"
echo -n "Catalog Manager (8080): "
curl -s http://localhost:8080/health > /dev/null 2>&1 && echo "✅ OK" || echo "❌ Not ready"

echo -n "Fault Manager (8081):   "
curl -s http://localhost:8081/health > /dev/null 2>&1 && echo "✅ OK" || echo "❌ Not ready"

echo -n "MCP Server (8090):      "
docker ps | grep mcp_server | grep -q "Up" && echo "✅ OK" || echo "❌ Not running"

echo ""
echo "🎯 Ready to run demo:"
echo "   python test_fault_management.py"

echo ""
echo "📝 If services aren't ready, wait another 10-20 seconds and try again."
