# Claude Desktop Setup Instructions

## Prerequisites

1. Make sure the MCP server is running:
```bash
cd /Users/joe/dev/mcp_cm_v1
make up
```

2. Verify it's working:
```bash
curl http://localhost:8090/health
```

## Configure Claude Desktop

1. Locate your Claude Desktop configuration file:
   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
   - **Linux**: `~/.config/Claude/claude_desktop_config.json`

2. Edit the configuration file and add the telepath-mcp server:

```json
{
  "mcpServers": {
    "telepath-mcp": {
      "command": "python3",
      "args": ["/Users/joe/dev/mcp_cm_v1/mcp_bridge.py"]
    }
  }
}
```

**Important**: Update the path `/Users/joe/dev/mcp_cm_v1/mcp_bridge.py` to match your actual directory.

3. Save the file and completely quit Claude Desktop (not just close the window)

4. Start Claude Desktop again

## Verify Connection

1. In Claude Desktop, you should see the MCP icon in the text input area
2. Click on it to see available tools:
   - service_qualification
   - customer_management  
   - product_ordering
   - service_activation

## Test the Tools

Try asking Claude to:
- "Check if fiber internet is available at 123 Main Street in Springfield"
- "Look up customer 8452934"
- "Create a fiber internet order for customer 8452936"

## Troubleshooting

If the connection fails:

1. Check that the bridge can run:
```bash
python3 /Users/joe/dev/mcp_cm_v1/mcp_bridge.py
```
You should see no output (it's waiting for input). Press Ctrl+C to exit.

2. Check Python dependencies:
```bash
pip3 install aiohttp
```

3. Check the Claude Desktop logs:
   - **macOS**: `~/Library/Logs/Claude/`
   - Look for errors related to "telepath-mcp"

4. Test the bridge manually:
```bash
# Terminal 1: Run the bridge
python3 /Users/joe/dev/mcp_cm_v1/mcp_bridge.py

# Terminal 2: Send a test message
echo '{"jsonrpc":"2.0","method":"initialize","params":{"protocolVersion":"2024-11-05"},"id":1}' | python3 /Users/joe/dev/mcp_cm_v1/mcp_bridge.py
```

## Alternative: Direct HTTP Configuration (Experimental)

If you want to try connecting Claude Desktop directly to the HTTP server without the bridge:

```json
{
  "mcpServers": {
    "telepath-mcp": {
      "url": "http://localhost:8090/mcp/stream",
      "transport": "http"
    }
  }
}
```

Note: This may not work as Claude Desktop typically expects stdio-based servers.
