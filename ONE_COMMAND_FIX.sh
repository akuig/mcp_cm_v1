#!/bin/bash
# ONE COMMAND TO FIX EVERYTHING

echo "🚀 ONE-COMMAND FIX FOR MCP HTTP STREAMING"
echo "========================================"
echo ""

# Make all scripts executable
chmod +x fix_fastapi_dependency.sh
chmod +x complete_http_fix.sh
chmod +x make_fix_executable.sh
chmod +x test_http_streaming.py

# Run the complete fix
./complete_http_fix.sh

# If successful, show final steps
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ SUCCESS! MCP HTTP server is running!"
    echo ""
    echo "📋 Copy this to Claude Desktop config:"
    echo "   (~/Library/Application Support/Claude/claude_desktop_config.json)"
    echo ""
    cat claude_desktop_config_http.json
    echo ""
    echo ""
    echo "Or run:"
    echo "  cp claude_desktop_config_http.json ~/Library/Application\\ Support/Claude/claude_desktop_config.json"
    echo ""
    echo "Then restart Claude Desktop!"
fi
