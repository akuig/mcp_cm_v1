# Troubleshooting Guide

## Fix Database Issues

If you see errors like "relation does not exist", the database needs to be initialized:

```bash
# Option 1: Reset database completely
make reset-db

# Option 2: Start fresh
make clean
make build
make reset-db
make up
```

## Using with MCP Inspector

The MCP Inspector requires the bridge to work with HTTP streaming:

```bash
# Terminal 1: Make sure services are running
make up

# Terminal 2: Run the bridge
python3 mcp_bridge.py

# Terminal 3: Run MCP Inspector
npx @anthropic/mcp-inspector stdio
```

## Using with Claude Desktop

1. First, ensure the server is running:
```bash
make up
```

2. Add to Claude Desktop configuration:
   - On macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - On Windows: `%APPDATA%\Claude\claude_desktop_config.json`

Add this server configuration:
```json
{
  "mcpServers": {
    "telepath-mcp": {
      "url": "http://localhost:8090/sse"
    }
  }
}
```

3. Restart Claude Desktop

4. You should see "telepath-mcp" in the MCP servers list when you start a new conversation

5. The server provides these tools:
   - **service_qualification** - Check service availability at a location
   - **customer_management** - Look up customer information
   - **product_ordering** - Create product orders
   - **service_activation** - Activate services

## Testing the Server

### Quick health check:
```bash
curl http://localhost:8090/health
```

### Test MCP protocol:
```bash
# Initialize
curl -X POST http://localhost:8090/mcp/stream \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "method": "initialize", "params": {"protocolVersion": "2024-11-05"}, "id": 1}'

# List tools
curl -X POST http://localhost:8090/mcp/stream \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "method": "tools/list", "params": {}, "id": 2}'
```

## Common Issues

### Port Already in Use
```bash
# Stop all containers
docker-compose down
# Check for processes using the ports
lsof -i :8080
lsof -i :8090
lsof -i :5432
```

### Container Won't Start
```bash
# Check logs
docker-compose logs mcp-server
docker-compose logs catalog-manager
docker-compose logs postgres
```

### Python Module Not Found
```bash
# Install dependencies
pip3 install aiohttp
# Or use virtual environment
make venv
source venv/bin/activate
pip install -r requirements_test.txt
```

## Verifying Everything Works

Run the full test suite:
```bash
make test-mcp
```

All tests should pass with output like:
```
📊 Test Summary:
   ✅ Passed: 6
   ❌ Failed: 0
   📈 Total: 6
```
