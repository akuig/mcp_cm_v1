# Fixed: FastAPI Dependency Missing

## The Problem
The MCP HTTP streaming server failed with:
```
ModuleNotFoundError: No module named 'fastapi'
```

## The Fix

### 1. Updated requirements_mcp.txt
Added:
- `fastapi>=0.104.0`
- `uvicorn[standard]>=0.24.0`

### 2. Quick Fix Script
```bash
chmod +x fix_fastapi_dependency.sh
./fix_fastapi_dependency.sh
```

This will:
- Rebuild the MCP container with FastAPI
- Restart the service
- Test the health endpoint

### 3. Alternative Solution
If issues persist, I've also created `mcp_simple_http_server.py` which uses Starlette directly (lighter weight than FastAPI).

## To Apply the Fix

```bash
# Option 1: Fix the current server
chmod +x fix_fastapi_dependency.sh && ./fix_fastapi_dependency.sh

# Option 2: Use the simpler server
docker-compose -f docker-compose-with-fault.yml exec mcp-server sed -i 's/mcp_http_streaming_server/mcp_simple_http_server/g' /app/entrypoint.sh
docker-compose -f docker-compose-with-fault.yml restart mcp-server
```

## What Changed
- ✅ Added FastAPI to requirements
- ✅ Created fix script
- ✅ Created alternative simple server

The server should now start successfully with HTTP endpoints!
