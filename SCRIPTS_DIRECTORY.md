# Fault Management Scripts Directory

## Fix Scripts (Use These First!)

| Script | Purpose | When to Use |
|--------|---------|------------|
| `complete_fix.sh` | **Complete rebuild and fix** | ⭐ Recommended - fixes all issues |
| `quick_start_workaround.sh` | Start without health checks | Quick workaround if rebuild takes too long |
| `fix_fault_manager.sh` | Fix just fault manager | If only fault manager has issues |
| `fix_mcp_server.sh` | Fix MCP server | If MCP server won't start |

## Diagnostic Scripts

| Script | Purpose |
|--------|---------|
| `diagnose_fault_manager.sh` | Detailed fault manager diagnostics |
| `check_services.py` | Basic service health check |
| `status_check.py` | Comprehensive status display |
| `test_fault_manager_local.py` | Test fault manager outside Docker |

## Demo Scripts

| Script | Purpose |
|--------|---------|
| `test_fault_management.py` | **Main demo script** |
| `run_fault_demo.sh` | Automated demo runner |

## Setup Scripts

| Script | Purpose |
|--------|---------|
| `setup_and_fix.sh` | Complete setup with fixes |
| `make_all_executable.sh` | Make all scripts executable |

## Quick Commands

```bash
# Fix everything and run demo
chmod +x make_all_executable.sh
./make_all_executable.sh
./complete_fix.sh
python test_fault_management.py

# Quick workaround
./quick_start_workaround.sh
python test_fault_management.py
```

## Files Changed
- `Dockerfile.fault` - Added curl for health checks
- `fault_manager.py` - Added /health endpoint
- `docker-compose-with-fault.yml` - Fixed health checks and dependencies
- `requirements_fault.txt` - Updated uvicorn

Total new scripts: 7
Total files modified: 4
