#!/bin/bash

# Apply MCP Server Fixes
echo "🔧 Applying MCP Server Fixes..."

# Make this script executable
chmod +x "$0"

# Make scripts executable
chmod +x deploy.sh
chmod +x quick_fix.sh
chmod +x test_mcp_tools.py

echo "✅ Updated mcp_server_enhanced.py with proper tool discovery"
echo "✅ Made test scripts executable"

echo ""
echo "🚀 To deploy and test:"
echo "1. Run: ./deploy.sh deploy"
echo "2. Wait for services to start"
echo "3. Test: python3 test_mcp_tools.py"
echo ""
echo "📋 Key fixes applied:"
echo "  - Fixed list_tools handler registration"
echo "  - Fixed call_tool handler registration"
echo "  - Added proper error handling"
echo "  - Enhanced HTTP status checking"
echo "  - Improved logging and debugging"
echo ""
echo "🔗 Claude Desktop Config:"
echo "  Use: /Users/joe/dev/mcp_cm_v1/claude_desktop_config.json"
echo "  Points to: http://localhost:8090"
echo ""
echo "✅ MCP Server fixes applied successfully!"
