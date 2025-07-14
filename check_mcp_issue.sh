#!/bin/bash
# Check container status

echo "Checking container status..."
docker-compose -f docker-compose-with-fault.yml ps

echo -e "\nChecking MCP server logs..."
docker-compose -f docker-compose-with-fault.yml logs mcp-server

echo -e "\nChecking if mcp_fastmcp_server_with_fault.py exists..."
ls -la mcp_fastmcp_server_with_fault.py

echo -e "\nChecking container details..."
docker ps -a | grep mcp_server
