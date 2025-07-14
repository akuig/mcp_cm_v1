# 🚀 Fault Management Demo - Complete Guide

## Quick Start (After MCP Fix)

```bash
# 1. Apply the fix and start everything
chmod +x setup_and_fix.sh
./setup_and_fix.sh

# 2. Check all services are running
python status_check.py

# 3. Run the demo
python test_fault_management.py
```

## What Was Fixed

The MCP server container wasn't starting because:
- ❌ **Dockerfile.mcp** didn't copy the new fault-enabled server file
- ❌ **docker-compose** had incorrect file paths and volume mounts

Fixed by:
- ✅ Updated Dockerfile.mcp to copy both server files
- ✅ Removed volume mounts and fixed command paths
- ✅ Removed deprecated 'version' attribute

## Available Scripts

| Script | Purpose |
|--------|---------|
| `setup_and_fix.sh` | Complete setup with MCP fix |
| `fix_mcp_server.sh` | Just fix and restart MCP server |
| `status_check.py` | Detailed service status check |
| `test_fault_management.py` | Run the fault demo |
| `check_services.py` | Basic service health check |
| `run_fault_demo.sh` | Automated demo runner |

## Service Endpoints

- **Catalog Manager**: http://localhost:8080
- **Fault Manager API**: http://localhost:8081/docs
- **MCP Server**: http://localhost:8090 (FastMCP protocol)
- **PostgreSQL**: localhost:5432

## Demo Scenario

1. 🏠 Jane Doe at 123 Main Street has fiber internet
2. 🚧 Construction work cuts fiber cable
3. 📞 Jane calls support
4. 🤖 AI Agent:
   - Detects the fiber cut
   - Reroutes traffic (15-min temp fix)
   - Creates trouble ticket
   - Dispatches technician
   - Sends SMS updates
5. ✅ Service fully restored in 4 hours

## Troubleshooting

If services don't start:
```bash
# Check logs
docker-compose -f docker-compose-with-fault.yml logs

# Rebuild everything
docker-compose -f docker-compose-with-fault.yml down -v
./setup_and_fix.sh
```

## Architecture with Fault Management

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Claude    │────▶│ MCP Server  │────▶│   Fault     │
│   Agent     │     │  (Enhanced) │     │  Manager    │
└─────────────┘     └─────────────┘     └─────────────┘
                           │                     │
                           ▼                     ▼
                    ┌─────────────┐      ┌─────────────┐
                    │  Catalog    │      │  Network    │
                    │  Manager    │      │  Faults &   │
                    └─────────────┘      │  Tickets    │
                           │             └─────────────┘
                           ▼
                    ┌─────────────┐
                    │ PostgreSQL  │
                    └─────────────┘
```

## Success Indicators

When everything is working:
- ✅ `status_check.py` shows all services green
- ✅ Fault simulation shows "Fiber cut on Main Street"
- ✅ Demo completes without errors
- ✅ Shows traffic rerouting and technician dispatch

---
Ready to demonstrate comprehensive telecom fault management with AI! 🎯
