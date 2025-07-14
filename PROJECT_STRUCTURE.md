# Telepath AI Demo - Project Structure

```
mcp_cm_v1/
├── 🐳 Docker Infrastructure (6 files)
│   ├── docker-compose.yml
│   ├── docker-compose-with-fault.yml
│   ├── Dockerfile.catalog
│   ├── Dockerfile.mcp
│   ├── Dockerfile.fault
│   └── Makefile
│
├── 🐍 Core Services (15 files)
│   ├── catalog_manager.py
│   ├── fault_manager.py
│   ├── mcp_fastmcp_server.py
│   ├── mcp_fastmcp_server_with_fault.py
│   ├── mcp_fastmcp_server_fault_simple.py
│   ├── mcp_stdio_server_fault.py
│   ├── mcp_http_streaming_server.py
│   ├── mcp_simple_http_server.py
│   ├── mcp_local_bridge.py
│   └── [6 other MCP variants]
│
├── 📋 Configuration Files (10 files)
│   ├── requirements_catalog.txt
│   ├── requirements_mcp.txt
│   ├── requirements_fault.txt
│   ├── claude_desktop_config.json
│   ├── claude_desktop_config_local.json
│   ├── claude_desktop_config_fault.json
│   ├── claude_desktop_config_http.json
│   └── init_db.sql
│
├── 🔧 Scripts (45+ files)
│   ├── Setup Scripts (10)
│   │   ├── setup.sh
│   │   ├── setup_fault_management.sh
│   │   ├── setup_claude_desktop.sh
│   │   └── setup_mcp_http_streaming.sh
│   │
│   ├── Fix Scripts (20)
│   │   ├── fix_mcp_server.sh
│   │   ├── fix_fault_manager.sh
│   │   ├── fix_mcp_asyncio.sh
│   │   ├── fix_claude_desktop.sh
│   │   ├── fix_http_streaming.sh
│   │   ├── fix_fastapi_dependency.sh
│   │   ├── complete_http_fix.sh
│   │   └── ONE_COMMAND_FIX.sh
│   │
│   └── Test/Diagnostic Scripts (15)
│       ├── test_fault_management.py
│       ├── test_http_streaming.py
│       ├── check_services.py
│       └── status_check.py
│
├── 📝 Documentation (40+ files)
│   ├── Main Docs (10)
│   │   ├── README.md
│   │   ├── FAULT_MANAGEMENT_README.md
│   │   ├── CLAUDE_DESKTOP_INTEGRATION.md
│   │   └── PROJECT_COMPLETE.md
│   │
│   ├── Fix Documentation (20)
│   │   ├── ASYNCIO_FIX_COMPLETE.md
│   │   ├── FASTAPI_FIXED.md
│   │   ├── HTTP_STREAMING_SUCCESS.md
│   │   └── [17 other fix docs]
│   │
│   └── Guides & References (10)
│       ├── QUICK_REFERENCE.md
│       ├── fault_demo_conversation.md
│       └── 100_FILES_MILESTONE.md
│
└── 🗄️ Database
    └── init_db.sql

Total: 104+ files
```

## By Technology
- **Python**: 60+ files
- **Shell Scripts**: 35+ files
- **Markdown Docs**: 40+ files
- **JSON Configs**: 7 files
- **Dockerfiles**: 3 files
- **SQL**: 1 file

## By Function
- **Core Demo**: 30 files
- **Fault Management**: 45 files
- **Claude Integration**: 29 files
- **Documentation**: 40+ files

---
**A complete telecom operations platform in 104+ files!** 🎯
