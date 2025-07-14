# Fix Applied for Fault Management Demo

## Issue
The test_fault_management.py script was failing with a JSONDecodeError because it was trying to call MCP tools directly via HTTP endpoints that don't exist in FastMCP.

## Root Cause
FastMCP uses the MCP protocol for communication with Claude, not direct HTTP endpoints. The test script was attempting to POST to `/tools/{tool_name}` which doesn't exist.

## Solution Applied
1. **Modified test_fault_management.py** to call Fault Manager APIs directly instead of going through MCP
2. **Added service health checks** before running the demo
3. **Created helper scripts** for easier deployment and troubleshooting

## Files Modified/Added
- `test_fault_management.py` - Fixed to call APIs directly
- `check_services.py` - Service health checker
- `run_fault_demo.sh` - Automated demo runner
- `QUICK_START_FAULT.md` - Simple instructions
- `FAULT_TROUBLESHOOTING.md` - Troubleshooting guide

## How to Run Now

### Option 1: Automated (Recommended)
```bash
chmod +x run_fault_demo.sh
./run_fault_demo.sh
```

### Option 2: Manual
```bash
# Start services
docker-compose -f docker-compose-with-fault.yml up -d

# Wait for initialization
sleep 20

# Check services are healthy
python check_services.py

# Run demo
python test_fault_management.py
```

## What the Demo Shows
1. Simulates a fiber cut on Main Street
2. Customer (Jane Doe) calls about service outage
3. Agent detects the fault and takes actions:
   - Reroutes traffic (15-min temporary fix)
   - Creates trouble ticket
   - Dispatches technician
   - Notifies customers
4. Shows full resolution process

## Note for Production
In production use with Claude Desktop:
- Claude would call these tools through the MCP protocol
- The test script bypasses MCP for demonstration purposes
- All the same functionality is available through the MCP tools
