# Fix for MCP Server Container Issue

## Problem
The MCP server container wasn't starting because:
1. The Dockerfile.mcp wasn't copying the new `mcp_fastmcp_server_with_fault.py` file
2. The docker-compose was trying to mount it as a volume and run it from the wrong path

## Solution Applied

### 1. Updated Dockerfile.mcp
- Now copies both `mcp_fastmcp_server.py` and `mcp_fastmcp_server_with_fault.py`
- Allows running either version

### 2. Updated docker-compose-with-fault.yml
- Removed the volume mount (not needed since files are copied in Dockerfile)
- Fixed the command to use the correct file path
- Removed unnecessary environment variable

### 3. Created fix_mcp_server.sh
A script that rebuilds and restarts everything properly

## To Fix and Run

```bash
# Make the fix script executable
chmod +x fix_mcp_server.sh

# Run the fix
./fix_mcp_server.sh

# After services are running, run the demo
python test_fault_management.py
```

## What Changed

**Before (broken):**
- Dockerfile only copied original server file
- docker-compose tried to mount and run from `/app/` path
- Container failed to start

**After (fixed):**
- Dockerfile copies both server files
- docker-compose runs the file directly (no volume mount)
- Container starts properly with fault management enabled
