#!/bin/bash

# Fix for TMF622 Data Format Issue
# This script fixes the Union[List, Dict] handling in the MCP server

set -e

echo "🔧 Fixing TMF622 Data Format Issue..."
echo "========================================="

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Step 1: Check if fixes are already applied
echo "Checking if fixes are already applied..."
if grep -q "Union\[List, Dict\]" mcp_fastmcp_server_extended.py; then
    print_status "Fixes already applied to mcp_fastmcp_server_extended.py"
else
    print_error "Fixes not properly applied. Please run this script again."
    exit 1
fi

# Step 2: Stop existing containers
echo ""
echo "Stopping existing containers..."
docker-compose down || true

# Step 3: Rebuild the MCP server container with the fixed code
echo ""
echo "Rebuilding MCP server container with fixes..."
docker-compose build mcp-server

# Step 4: Start all services
echo ""
echo "Starting all services..."
docker-compose up -d

# Step 5: Wait for services to be healthy
echo ""
echo "Waiting for services to be healthy..."
sleep 5

# Step 6: Check container status
echo ""
echo "Checking container status..."
docker-compose ps

# Step 7: Test the fix with a curl command
echo ""
echo "Testing the order_management endpoint..."
sleep 3

# Test listing orders (should return an array)
echo "Testing list orders (should return array):"
curl -s -X GET "http://localhost:8080/tmf622/productOrder?limit=3" | python3 -m json.tool | head -20 || print_warning "Could not test endpoint"

echo ""
echo "========================================="
print_status "Fix deployment complete!"
echo ""
echo "📋 What was fixed:"
echo "  • order_management now returns Union[List, Dict] instead of just Dict"
echo "  • log_audit now handles both list and dict responses"
echo "  • Status detection works correctly for list responses"
echo ""
echo "🧪 To verify the fix:"
echo "  1. Use MCP Inspector: ./run_inspector.sh"
echo "  2. Call order_management tool without orderId → should return list"
echo "  3. Call order_management with orderId → should return single dict"
echo ""
echo "🔄 For Claude Desktop:"
echo "  1. Restart Claude Desktop to pick up the changes"
echo "  2. The order_management tool should now work correctly"
echo ""

# Step 8: Check logs for any errors
echo "Recent MCP server logs:"
docker logs mcp_server --tail 10 2>&1 | grep -E "(ERROR|Warning|Started)" || true
