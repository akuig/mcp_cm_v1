#!/bin/bash
# Make HTTP streaming scripts executable

echo "Making HTTP streaming scripts executable..."

chmod +x setup_mcp_http_streaming.sh
chmod +x fix_http_streaming.sh
chmod +x test_http_streaming.py

echo "✅ HTTP streaming scripts are now executable!"
echo ""
echo "To setup HTTP streaming for Claude Desktop:"
echo "  ./fix_http_streaming.sh"
