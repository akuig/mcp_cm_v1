#!/bin/bash
# Script to run MCP Inspector with the HTTP streaming bridge

echo "Starting MCP Inspector Bridge for HTTP Streaming Server..."
echo "Make sure the MCP server is running on http://localhost:8090"
echo ""

# Check if mcp-inspector is installed
if ! command -v mcp-inspector &> /dev/null; then
    echo "MCP Inspector not found. Installing..."
    npm install -g @anthropic/mcp-inspector
fi

# Run the bridge
echo "Starting bridge..."
python mcp_bridge.py
