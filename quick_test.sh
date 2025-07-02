#!/bin/bash
# Quick test script to verify MCP server is working

echo "Testing MCP Server..."
echo ""

# Test 1: Health check
echo "1. Health Check:"
curl -s http://localhost:8090/health | jq .
echo ""

# Test 2: Initialize
echo "2. Initialize MCP:"
curl -s -X POST http://localhost:8090/mcp/stream \
  -H "Content-Type: application/json" \
  -H "Accept: application/json-stream" \
  -d '{"jsonrpc": "2.0", "method": "initialize", "params": {}, "id": 1}' | jq .
echo ""

# Test 3: List tools
echo "3. List Tools:"
curl -s -X POST http://localhost:8090/mcp/stream \
  -H "Content-Type: application/json" \
  -H "Accept: application/json-stream" \
  -d '{"jsonrpc": "2.0", "method": "tools/list", "params": {}, "id": 2}' | jq .
echo ""

# Test 4: Call a tool
echo "4. Test Service Qualification:"
curl -s -X POST http://localhost:8090/mcp/stream \
  -H "Content-Type: application/json" \
  -H "Accept: application/json-stream" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "service_qualification",
      "arguments": {
        "address": {
          "streetName": "Main Street",
          "streetNumber": "123",
          "city": "Springfield"
        },
        "serviceSpecification": {
          "id": "fiber500",
          "name": "Fiber 500 Mbps Plan"
        }
      }
    },
    "id": 3
  }' | jq .
