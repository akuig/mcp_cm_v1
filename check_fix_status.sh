#!/bin/bash

# Quick status check for TMF622 data format fix

echo "📊 TMF622 Data Format Fix Status Check"
echo "======================================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Check if fix is applied in the source file
echo "1. Checking source file for fixes..."
if grep -q "Union\[List, Dict\]" mcp_fastmcp_server_extended.py 2>/dev/null; then
    echo -e "   ${GREEN}✓${NC} Union[List, Dict] found in mcp_fastmcp_server_extended.py"
    
    # Check specific function
    if grep -A 2 "async def order_management" mcp_fastmcp_server_extended.py | grep -q "Union\[List, Dict\]"; then
        echo -e "   ${GREEN}✓${NC} order_management function has correct return type"
    else
        echo -e "   ${RED}✗${NC} order_management function still needs fix"
    fi
    
    # Check log_audit
    if grep "def log_audit" mcp_fastmcp_server_extended.py | grep -q "Union\[Dict, List\]"; then
        echo -e "   ${GREEN}✓${NC} log_audit function handles Union types"
    else
        echo -e "   ${YELLOW}⚠${NC} log_audit may need updating"
    fi
else
    echo -e "   ${RED}✗${NC} Fix not applied to source file"
fi

echo ""
echo "2. Checking Docker deployment..."
if docker ps | grep -q mcp_server; then
    echo -e "   ${GREEN}✓${NC} MCP server container is running"
    
    # Check if the fix is in the running container
    echo "   Checking deployed code in container..."
    if docker exec mcp_server grep -q "Union\[List, Dict\]" mcp_server.py 2>/dev/null; then
        echo -e "   ${GREEN}✓${NC} Fix is deployed in running container"
    else
        echo -e "   ${YELLOW}⚠${NC} Container may need rebuild with: ./fix_data_format_issue.sh"
    fi
else
    echo -e "   ${RED}✗${NC} MCP server container not running"
    echo "   Run: docker-compose up -d"
fi

echo ""
echo "3. Testing TMF622 endpoint..."
if curl -s http://localhost:8080/tmf622/productOrder?limit=1 >/dev/null 2>&1; then
    response=$(curl -s http://localhost:8080/tmf622/productOrder?limit=1)
    if [[ $response == \[* ]]; then
        echo -e "   ${GREEN}✓${NC} Endpoint returns array format correctly"
    else
        echo -e "   ${YELLOW}⚠${NC} Endpoint response format unclear"
    fi
else
    echo -e "   ${RED}✗${NC} Cannot reach TMF622 endpoint"
fi

echo ""
echo "======================================"
echo "📋 Summary:"
echo ""

# Determine overall status
if grep -q "Union\[List, Dict\]" mcp_fastmcp_server_extended.py 2>/dev/null && \
   docker ps | grep -q mcp_server && \
   docker exec mcp_server grep -q "Union\[List, Dict\]" mcp_server.py 2>/dev/null; then
    echo -e "${GREEN}✅ Fix is fully applied and deployed!${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Restart Claude Desktop"
    echo "2. Test order_management tool"
else
    echo -e "${YELLOW}⚠️  Fix needs to be deployed${NC}"
    echo ""
    echo "To apply the fix:"
    echo "1. Run: ./fix_data_format_issue.sh"
    echo "2. Wait for services to restart"
    echo "3. Run this check again"
fi

echo ""
echo "For detailed testing, run: python3 test_data_format_fix.py"
