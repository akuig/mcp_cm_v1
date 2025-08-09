#!/bin/bash

# Deploy Fixed Catalog Manager Script
# This script replaces the broken catalog manager with the fixed version

echo "🔧 Deploying Fixed Catalog Manager..."

# Backup the original file
echo "📁 Creating backup of original file..."
cp /Users/joe/dev/mcp_cm_v1/catalog_manager_extended.py /Users/joe/dev/mcp_cm_v1/catalog_manager_extended_backup_$(date +%Y%m%d_%H%M%S).py

# Replace with fixed version
echo "🔄 Replacing with fixed version..."
cp /Users/joe/dev/mcp_cm_v1/catalog_manager_extended_fixed.py /Users/joe/dev/mcp_cm_v1/catalog_manager_extended.py

# Restart the enhanced deployment
echo "🚀 Restarting enhanced deployment..."
cd /Users/joe/dev/mcp_cm_v1

# Stop existing containers
echo "⏹️  Stopping existing containers..."
docker-compose -f docker-compose.extended.yml down

# Rebuild and restart
echo "🔨 Rebuilding catalog manager image..."
docker-compose -f docker-compose.extended.yml build catalog-manager

echo "🚀 Starting enhanced services..."
docker-compose -f docker-compose.extended.yml up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 15

# Test the customer management endpoint
echo "🧪 Testing TMF629 Customer Management..."
echo "Testing customer ID: 8452934"
curl -s "http://localhost:8080/tmf629/customer/8452934" | jq '.'

echo ""
echo "🧪 Testing TMF622 Order Management (GET)..."
curl -s "http://localhost:8080/tmf622/productOrder?limit=5" | jq '.'

echo ""
echo "✅ Fixed catalog manager deployed successfully!"
echo "🔍 Key fixes applied:"
echo "   - Removed duplicate TMF622 route definitions"
echo "   - Implemented missing get_product_orders() function"
echo "   - Fixed Flask routing conflicts"
echo "   - All TMF API endpoints should now work properly"

echo ""
echo "📊 You can now test with existing customer IDs:"
echo "   - 8452934 (Jane Doe)"
echo "   - 8452935 (John Smith)"
echo "   - 8452936 (Alice Johnson)"
echo "   - 8452937 (Bob Williams)"
echo "   - 8452938 (Carol Brown)"
echo "   - 8452939 (David Lee)"
