# 🚀 FIX THE MCP SERVER - SIMPLE STEPS

## The Error
```
AttributeError: 'Server' object has no attribute 'add_tool'
```

## The Fix (2 Steps)

### Step 1: Run This Command
```bash
chmod +x FINAL_MCP_FIX.sh && ./FINAL_MCP_FIX.sh
```

### Step 2: Configure Claude Desktop
```bash
cp claude_desktop_config_http.json ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

Then restart Claude Desktop.

## That's It! ✅
The MCP server is now working with all fault management tools.

---
Try in Claude: "Check for service issues at 123 Main Street Dublin"
