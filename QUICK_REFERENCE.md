# 🚀 Telepath AI Demo - Quick Reference

## Start Everything
```bash
docker-compose -f docker-compose-with-fault.yml up -d
```

## Setup Claude Desktop (HTTP Streaming)
```bash
chmod +x fix_http_streaming.sh && ./fix_http_streaming.sh
cp claude_desktop_config_http.json ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

## Test Components
```bash
# Backend services
curl http://localhost:8080/health  # Catalog Manager
curl http://localhost:8081/health  # Fault Manager
curl http://localhost:8090/health  # MCP Server

# Full demo
python test_fault_management.py

# Claude connection
python test_http_streaming.py
```

## Claude Desktop Usage
1. Restart Claude Desktop after config
2. Look for "telepath-fault-http" in MCP connections
3. Try: "Check for service issues at 123 Main Street Dublin"

## Key URLs
- Catalog API: http://localhost:8080
- Fault API: http://localhost:8081/docs
- MCP Stream: http://localhost:8090/mcp

## Available Tools
- service_qualification
- customer_management
- product_ordering
- service_activation
- check_service_status ⚡
- create_trouble_ticket 🎫
- execute_remedial_action 🔧
- get_service_problems 📍

## Stop Everything
```bash
docker-compose -f docker-compose-with-fault.yml down
```

## Logs
```bash
docker-compose -f docker-compose-with-fault.yml logs -f
```

---
Ready to demo! 🎯
