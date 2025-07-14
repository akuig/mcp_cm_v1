#!/bin/bash
# Quick fix for Claude Desktop HTTP Streaming

echo "🚀 Quick Fix: MCP HTTP Streaming for Claude Desktop"
echo "================================================="
echo ""

# Make setup script executable
chmod +x setup_mcp_http_streaming.sh

# Run the setup
./setup_mcp_http_streaming.sh

# If successful, provide final instructions
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ MCP HTTP Streaming server is ready!"
    echo ""
    echo "📝 Final step:"
    echo "   cp claude_desktop_config_http.json ~/Library/Application\\ Support/Claude/claude_desktop_config.json"
    echo ""
    echo "Then restart Claude Desktop and connect to 'telepath-fault-http'"
else
    echo ""
    echo "❌ Setup failed. Check the errors above."
fi
