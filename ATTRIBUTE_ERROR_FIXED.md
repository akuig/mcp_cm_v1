# Fixed: AttributeError 'Server' object has no attribute 'add_tool'

## The Problem
The MCP simple server was using incorrect SDK methods:
```python
server.add_tool(...)  # ❌ This method doesn't exist
```

## The Solution
Created `mcp_working_http_server.py` that uses the correct MCP SDK patterns:
```python
@mcp_server.list_tools()  # ✅ Correct decorator
@mcp_server.call_tool()   # ✅ Correct decorator
```

## What I Fixed

### 1. Created Working HTTP Server
- `mcp_working_http_server.py` - Properly implements MCP protocol
- Uses decorators for tool registration
- Implements all required endpoints:
  - `/health` - Health check
  - `/mcp` - MCP info
  - `/mcp/stream` - JSON-RPC streaming
  - `/mcp/sse` - Server-sent events

### 2. Proper Tool Implementation
- All 8 tools properly registered
- Correct request/response handling
- Error handling for each tool

### 3. Updated Configuration
- `docker-compose-with-fault.yml` - Uses working server
- `Dockerfile.mcp` - Includes new server file

## Quick Fix

```bash
chmod +x fix_attribute_error.sh && ./fix_attribute_error.sh
```

This will:
1. Rebuild with the working server
2. Restart the MCP container
3. Test all endpoints
4. Show Claude Desktop config

## Testing

```bash
# Test the endpoints
python test_working_mcp.py

# Check health
curl http://localhost:8090/health

# Check MCP info
curl http://localhost:8090/mcp
```

## Claude Desktop Configuration

```json
{
  "mcpServers": {
    "telepath-fault-http": {
      "url": "http://localhost:8090/mcp"
    }
  }
}
```

## Result
✅ MCP server now properly implements the protocol
✅ All tools available via HTTP streaming
✅ Ready for Claude Desktop connection
✅ No more AttributeError!
