#!/bin/bash

echo "🔍 Debugging MCP Server - Agent shows no tools"
echo "=============================================="

# Check if MCP server is running
echo "📊 Container Status:"
docker-compose ps mcp-server

echo ""
echo "📋 Recent MCP Server Logs:"
echo "========================="
docker-compose logs --tail=30 mcp-server

echo ""
echo "🧪 Testing MCP Endpoints:"
echo "========================"

# Test health endpoint
echo "• Health endpoint:"
curl -s http://localhost:8090/health | jq . 2>/dev/null || curl -s http://localhost:8090/health

echo ""
echo "• MCP info endpoint:"
curl -s http://localhost:8090/mcp | jq . 2>/dev/null || curl -s http://localhost:8090/mcp

echo ""
echo "• Testing tools/list JSON-RPC call:"
curl -s -X POST http://localhost:8090/mcp/stream \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/list",
    "id": 1
  }' | jq . 2>/dev/null || curl -s -X POST http://localhost:8090/mcp/stream \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/list",
    "id": 1
  }'

echo ""
echo "• Testing initialize call:"
curl -s -X POST http://localhost:8090/mcp/stream \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "initialize",
    "id": 1,
    "params": {}
  }' | jq . 2>/dev/null || curl -s -X POST http://localhost:8090/mcp/stream \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "initialize",
    "id": 1,
    "params": {}
  }'

echo ""
echo "🔍 If tools are empty, checking for errors in the response..."