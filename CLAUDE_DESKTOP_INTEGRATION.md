# Claude Desktop Integration Guide

## The Issue
Claude Desktop is trying to connect via ngrok to endpoints like `/mcp/stream` and `/mcp/sse`, but our MCP server uses STDIO protocol, not HTTP endpoints.

## Solution
Use STDIO-based MCP server that Claude Desktop can communicate with properly.

## Quick Setup (Local Python)

1. **Ensure services are running locally:**
```bash
docker-compose -f docker-compose-with-fault.yml up -d
```

2. **Install MCP SDK locally:**
```bash
pip install mcp aiohttp
```

3. **Copy Claude Desktop config:**
```bash
cp claude_desktop_config_local.json ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

4. **Restart Claude Desktop**

## Alternative Setup (Docker)

1. **Build and setup:**
```bash
chmod +x setup_claude_desktop.sh
./setup_claude_desktop.sh
```

2. **Follow the instructions printed**

## Configuration Files

### Option 1: Local Python (Recommended)
- Uses `mcp_local_bridge.py` 
- Runs on your host machine
- Connects to Docker services on localhost
- File: `claude_desktop_config_local.json`

### Option 2: Docker Container
- Uses `mcp_stdio_server_fault.py`
- Runs inside Docker container
- File: `claude_desktop_config_fault.json`

## Testing the Connection

1. **Check services are running:**
```bash
curl http://localhost:8080/health  # Catalog Manager
curl http://localhost:8081/health  # Fault Manager
```

2. **Test MCP server manually:**
```bash
echo '{"jsonrpc": "2.0", "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}}, "id": 1}' | \
python3 mcp_local_bridge.py
```

## Troubleshooting

### "Connection failed" in Claude Desktop
- Make sure services are running on localhost (not ngrok)
- Check Claude Desktop logs: `~/Library/Logs/Claude/`
- Verify Python path in config file

### "Module not found" errors
```bash
pip install mcp aiohttp
export PYTHONPATH=/Users/joe/dev/mcp_cm_v1:$PYTHONPATH
```

### Services not accessible
- Don't use ngrok - services must be on localhost
- Check Docker is running: `docker ps`
- Restart services: `docker-compose -f docker-compose-with-fault.yml restart`

## Available Tools

Once connected, these tools will be available in Claude:

1. **service_qualification** - Check service availability at an address
2. **customer_management** - Get customer information
3. **product_ordering** - Create product orders
4. **service_activation** - Activate services
5. **check_service_status** - Check for network faults ⚡
6. **create_trouble_ticket** - Create trouble tickets 🎫
7. **execute_remedial_action** - Execute fixes 🔧
8. **get_service_problems** - List area problems 📍

## Demo Scenario

Ask Claude to:
"Check if there are any service issues at 123 Main Street in Dublin"

Claude will use the tools to detect the fiber cut and offer remediation options!
