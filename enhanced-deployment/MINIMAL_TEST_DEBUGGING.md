# Minimal Test Approach for Claude MCP Debugging

## Current Status

Claude connects successfully and protocol version negotiation works (`2025-06-18`), but Claude still doesn't request the tools list. The 12-tool enhanced server works with MCP Inspector but not with Claude.

## Testing Strategy

### Phase 1: Minimal Single Tool Test

I've created a minimal test server (`mcp_server_minimal.py`) with:
- **Only 1 tool**: `service_qualification`
- **Simplified capabilities**: Just `{"tools": {"listChanged": True}}`
- **Enhanced logging**: Special message when Claude requests tools list
- **Same protocol fix**: Supports Claude's `2025-06-18` protocol version

### Purpose of Minimal Test

This will help determine if the issue is:
1. **Tool complexity**: Too many tools or complex schemas overwhelming Claude
2. **JSON schema validation**: One of the 12 tools has invalid schema
3. **Protocol issue**: Still something wrong with the MCP handshake
4. **Capabilities format**: Claude expects different capabilities structure

### Files Created

1. **`mcp_server_minimal.py`** - Single tool test server
2. **`test_minimal_server.sh`** - Deployment script for minimal test

### Deployment

```bash
cd /Users/joe/dev/mcp_cm_v1/enhanced-deployment
chmod +x test_minimal_server.sh
./test_minimal_server.sh
```

### Expected Outcomes

#### ✅ If Minimal Test Works
- Claude requests tools list (logs show: `🎉 CLAUDE REQUESTED TOOLS LIST! 🎉`)
- Claude sees the single tool
- **Conclusion**: Issue is with tool complexity/schemas in 12-tool version

#### ❌ If Minimal Test Fails
- Claude still doesn't request tools list
- **Conclusion**: Issue is with MCP protocol implementation or capabilities

### Next Steps Based on Results

#### If Minimal Works ✅
1. Add tools one by one to identify which tool breaks Claude
2. Validate JSON schemas for all 12 tools
3. Look for invalid characters or malformed schemas
4. Test with 4 original tools vs 8 new catalog tools

#### If Minimal Fails ❌
1. Compare exact JSON-RPC messages with working original server
2. Check if capabilities structure needs modification
3. Verify MCP protocol specification compliance
4. Test with even simpler capabilities or server info

### Debug Logging

The minimal server includes enhanced logging:
- Clear identification when Claude requests tools
- Protocol version negotiation details  
- Exact JSON request/response logging
- Special celebration message if Claude requests tools list

### Verification Commands

```bash
# Watch logs in real-time
docker compose logs -f mcp-server

# Check for specific success pattern
docker compose logs mcp-server | grep "CLAUDE REQUESTED TOOLS"

# Health check
curl http://localhost:8090/health | jq '.'
```

This systematic approach should help isolate whether the issue is in the tool definitions or the core MCP protocol implementation.
