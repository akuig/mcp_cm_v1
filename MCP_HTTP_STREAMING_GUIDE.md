# MCP HTTP Streaming for Claude Desktop

## Overview
Claude Desktop supports MCP via HTTP streaming, which is what the ngrok logs were showing:
- `/mcp/stream` - HTTP streaming endpoint
- `/mcp/sse` - Server-Sent Events endpoint

## Solution
Created a proper HTTP streaming MCP server using FastMCP with FastAPI integration.

## Quick Setup

```bash
# 1. Make script executable and run
chmod +x setup_mcp_http_streaming.sh
./setup_mcp_http_streaming.sh

# 2. Test the endpoints
python test_http_streaming.py

# 3. Configure Claude Desktop
cp claude_desktop_config_http.json ~/Library/Application\ Support/Claude/claude_desktop_config.json

# 4. Restart Claude Desktop
```

## Architecture

```
Claude Desktop <--HTTP--> MCP Server <--HTTP--> Backend Services
    (Mac)       Streaming  (Port 8090)          (Ports 8080/8081)
                 /mcp/*                         Catalog & Fault Mgr
```

## Key Endpoints

- **Base URL**: `http://localhost:8090`
- **Health Check**: `http://localhost:8090/health`
- **MCP Stream**: `http://localhost:8090/mcp/stream`
- **MCP SSE**: `http://localhost:8090/mcp/sse`
- **MCP Info**: `http://localhost:8090/mcp`

## Configuration

The Claude Desktop config uses:
```json
{
  "mcpServers": {
    "telepath-fault-http": {
      "url": "http://localhost:8090/mcp",
      "description": "Telepath AI MCP Server with Fault Management (HTTP Streaming)"
    }
  }
}
```

## Available Tools

1. **Original TMF Tools**:
   - `service_qualification` - Check service availability
   - `customer_management` - Get customer info
   - `product_ordering` - Create orders
   - `service_activation` - Activate services

2. **Fault Management Tools**:
   - `check_service_status` - Detect network faults
   - `create_trouble_ticket` - Create trouble tickets
   - `execute_remedial_action` - Execute fixes
   - `get_service_problems` - List area problems

## Testing

1. **Test Health**:
```bash
curl http://localhost:8090/health
```

2. **Test with Script**:
```bash
python test_http_streaming.py
```

3. **In Claude Desktop**:
Ask: "Check for service issues at 123 Main Street Dublin"

## Troubleshooting

### If Claude can't connect:
1. Ensure NO ngrok - use localhost directly
2. Check MCP server logs:
   ```bash
   docker-compose -f docker-compose-with-fault.yml logs mcp-server
   ```
3. Verify endpoints are accessible:
   ```bash
   curl http://localhost:8090/health
   ```

### Port conflicts:
```bash
# Check what's using port 8090
lsof -i :8090

# Stop and restart
docker-compose -f docker-compose-with-fault.yml down
docker-compose -f docker-compose-with-fault.yml up -d
```

## Implementation Details

The HTTP streaming server (`mcp_http_streaming_server.py`):
- Uses FastMCP with FastAPI integration
- Implements proper `/mcp/*` endpoints
- Supports both streaming and SSE
- All tools are decorated with `@mcp.tool()`
- Returns JSON formatted responses

## Success Indicators

When working correctly:
- Health endpoint returns `{"transport": "http-streaming"}`
- Claude Desktop shows "telepath-fault-http" as connected
- Tools appear in Claude's interface
- No ngrok errors in logs
