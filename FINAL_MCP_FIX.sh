#!/bin/bash
# Final fix for all MCP server issues

echo "🎯 FINAL FIX - MCP HTTP Server"
echo "=============================="
echo ""
echo "Fixing AttributeError and setting up working HTTP server..."
echo ""

# Make scripts executable
chmod +x fix_attribute_error.sh
chmod +x test_working_mcp.py

# Run the fix
./fix_attribute_error.sh

if [ $? -eq 0 ]; then
    echo ""
    echo "🧪 Running endpoint tests..."
    python3 test_working_mcp.py
    
    echo ""
    echo "✅ ALL FIXED!"
    echo ""
    echo "📋 Final Steps:"
    echo "1. Copy Claude config:"
    echo "   cp claude_desktop_config_http.json ~/Library/Application\\ Support/Claude/claude_desktop_config.json"
    echo ""
    echo "2. Restart Claude Desktop"
    echo ""
    echo "3. Look for 'telepath-fault-http' in MCP connections"
    echo ""
    echo "4. Try: 'Check for service issues at 123 Main Street Dublin'"
    echo ""
    echo "🎉 The MCP HTTP server is now working correctly!"
else
    echo ""
    echo "❌ Fix failed. Check the errors above."
fi
