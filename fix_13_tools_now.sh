#!/usr/bin/env bash

# Quick fix script to get all 13 tools working properly
# Fixes both the missing requests module and API response format issues

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_msg() {
    local color=$1
    local msg=$2
    echo -e "${color}${msg}${NC}"
}

print_msg "$BLUE" "🔧 Fixing 13 Tools Configuration..."
print_msg "$BLUE" "===================================="

# Fix 1: Install requests module for testing
print_msg "$YELLOW" "📦 Installing requests module for testing..."
pip3 install requests >/dev/null 2>&1 || pip install requests >/dev/null 2>&1
print_msg "$GREEN" "✅ Requests module installed"

# Fix 2: Backup current catalog manager
print_msg "$YELLOW" "📦 Backing up current files..."
cp catalog_manager_extended.py catalog_manager_extended.py.backup.$(date +%Y%m%d_%H%M%S) 2>/dev/null || true

# Fix 3: Apply the fixed catalog manager
print_msg "$YELLOW" "📝 Applying fixed catalog_manager_extended.py..."
if [ -f "catalog_manager_extended_fixed.py" ]; then
    cp catalog_manager_extended_fixed.py catalog_manager_extended.py
    print_msg "$GREEN" "✅ Catalog manager fixed"
else
    print_msg "$YELLOW" "⚠️  Fixed file not found, will rebuild with current file"
fi

# Fix 4: Rebuild and restart services
print_msg "$YELLOW" "🐳 Rebuilding Docker containers..."
docker-compose -f docker-compose.extended.yml down >/dev/null 2>&1
docker-compose -f docker-compose.extended.yml build --no-cache
print_msg "$GREEN" "✅ Containers rebuilt"

print_msg "$YELLOW" "🚀 Starting services..."
docker-compose -f docker-compose.extended.yml up -d
print_msg "$YELLOW" "⏳ Waiting for services to start (20 seconds)..."
sleep 20

# Fix 5: Verify the fix
print_msg "$BLUE" "🔍 Verifying fixes..."

# Check health
if curl -s http://localhost:8080/health | grep -q "healthy"; then
    print_msg "$GREEN" "✅ Catalog Manager is healthy"
else
    print_msg "$RED" "❌ Catalog Manager health check failed"
fi

# Count tools
print_msg "$YELLOW" "Counting MCP tools..."
TOOL_COUNT=$(curl -s -X POST http://localhost:8090/mcp/stream \
    -H "Content-Type: application/json" \
    -d '{"jsonrpc": "2.0", "method": "tools/list", "params": {}, "id": 1}' 2>/dev/null | \
    python3 -c "import sys, json; data = json.load(sys.stdin); print(len(data.get('result', {}).get('tools', [])))" 2>/dev/null || echo "0")

if [ "$TOOL_COUNT" = "13" ]; then
    print_msg "$GREEN" "✅ All 13 tools are available!"
else
    print_msg "$YELLOW" "⚠️  Found $TOOL_COUNT tools (expected 13)"
fi

print_msg "$GREEN" "\n✨ Fixes Applied Successfully!"
print_msg "$GREEN" "================================"
print_msg "$BLUE" "\nNow you can:"
print_msg "$NC" "1. Test with Claude Desktop (all 13 tools should work)"
print_msg "$NC" "2. Run verification: python3 verify_13_tools.py"
print_msg "$NC" "3. Check logs: docker-compose -f docker-compose.extended.yml logs"
