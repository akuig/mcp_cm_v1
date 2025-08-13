# Telepath AI Demo System - Enhanced Catalog Manager

A demonstration system for the Telepath AI project that exposes telecommunications BSS/OSS systems through Model Context Protocol (MCP) servers, enabling autonomous operation by AI agents.

## 🚀 Version 2.0 - Enhanced with 13 MCP Tools

This enhanced version extends the original 4 tools to a comprehensive set of 13 tools, adding advanced catalog management capabilities while maintaining full backward compatibility.

## Overview

This MVP implements a complete telecommunications catalog management system with:
- **13 MCP Tools** - Extended from 4 to 13 tools for comprehensive catalog management
- **FastMCP Server** with HTTP streaming transport (Claude Desktop compatible)
- **Enhanced Catalog Manager** implementing TM Forum APIs
- **PostgreSQL Database** with extended schema and sample data
- **Docker-based Deployment** for easy setup and scaling

## ✨ Key Features

- **13 MCP Tools**: Complete set of TMF Forum and catalog management tools
- **HTTP Streaming Transport**: FastMCP's streamable-http for real-time communication
- **TM Forum API Integration**: Full implementation of TMF622, TMF629, TMF637, TMF640
- **Catalog Management APIs**: Service specifications, product offerings, geographic coverage
- **Full Audit Logging**: Compliance-ready operation logging
- **Docker Deployment**: One-command deployment with docker-compose

## 🏗️ Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Claude/AI     │────▶│  MCP Server     │────▶│ Catalog Manager │
│   (Client)      │HTTP │  (13 Tools)     │HTTP │  (Enhanced APIs)│
│                 │Stream│  Port 8090     │     │   Port 8080     │
└─────────────────┘     └─────────────────┘     └────────┬────────┘
                                                          │
                        ┌─────────────────────────────────┼────────┐
                        │                                 ▼        │
                        │                        ┌─────────────────┐
                        │  Extended Schema:     │   PostgreSQL    │
                        │  • Customers          │    Database     │
                        │  • Service Specs      │   Port 5432     │
                        │  • Product Offerings  └─────────────────┘
                        │  • Geographic Locations                 │
                        │  • Coverage Data                        │
                        │  • Orders & Activations                 │
                        └──────────────────────────────────────────┘
```

## 🛠️ Available MCP Tools (13 Total)

### TMF Forum Standard APIs (5 tools)

| Tool | API | Description |
|------|-----|-------------|
| **service_qualification** | TMF637 | Check if a service is available at a specific location |
| **customer_management** | TMF629 | Get customer information including account status |
| **product_ordering** | TMF622 | Create and manage product orders |
| **service_activation** | TMF640 | Activate services in the network |
| **order_management** | TMF622 | List and retrieve product orders with filtering |

### Catalog Management Tools (8 tools)

| Tool | Description |
|------|-------------|
| **list_service_specifications** | List/filter all available service specifications |
| **list_product_offerings** | List/filter product offerings with pricing |
| **list_geographic_locations** | List locations with service coverage information |
| **sync_catalog_data** | Validate and synchronize catalog integrity |
| **create_service_specification** | Create new service specifications |
| **create_product_offering** | Create new product offerings |
| **link_offering_to_specification** | Link products to service specifications |
| **add_geographic_coverage** | Add service coverage for geographic areas |

## 📁 Key Files

### Core Python Files
```
mcp_fastmcp_server_extended.py   # MCP server with all 13 tools
catalog_manager_extended.py       # Enhanced catalog manager API
verify_13_tools.py               # Verification script for all tools
```

### Docker Configuration
```
Dockerfile.catalog.enhanced      # Catalog manager container
Dockerfile.mcp.enhanced         # MCP server container
docker-compose.extended.yml     # Enhanced orchestration config
```

### Database & Requirements
```
init_db_extended.sql            # Extended database schema
requirements_catalog.txt        # Catalog manager dependencies
requirements_mcp.txt           # MCP server dependencies
requirements_test.txt          # Testing dependencies
```

### Build & Deployment Scripts
```
Makefile.enhanced13            # Enhanced Makefile with all commands
apply_enhanced_updates.sh      # Apply updates to existing deployment
fix_13_tools_now.sh           # Quick fix script
build_enhanced.sh             # Cross-platform build script
deploy_enhanced_cm.sh         # One-command deployment
```

## 🚀 Quick Start

### Prerequisites
- Docker 20.10+ and Docker Compose 2.0+
- Python 3.9+ with pip
- 4GB RAM minimum (8GB recommended)
- Ports 8080, 8090, and 5432 available

### Installation - Enhanced Version

1. **Clone and setup:**
```bash
git clone <repository-url> mcp_cm_v1
cd mcp_cm_v1
chmod +x *.sh
```

2. **Build the enhanced version:**
```bash
# Using the enhanced Makefile
make -f Makefile.enhanced13 setup
make -f Makefile.enhanced13 build
make -f Makefile.enhanced13 up

# OR using docker-compose directly
docker-compose -f docker-compose.extended.yml build --no-cache
docker-compose -f docker-compose.extended.yml up -d
```

3. **Verify deployment (wait 20 seconds after startup):**
```bash
# Check health
curl http://localhost:8080/health

# Verify 13 tools
python3 verify_13_tools.py

# OR manually count tools
curl -X POST http://localhost:8090/mcp/stream \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "method": "tools/list", "params": {}, "id": 1}' | \
  jq '.result.tools | length'
# Should output: 13
```

## 🔧 Build from Scratch (New Server)

### Option 1: Automated Script
```bash
# Download and run the build script
wget https://your-repo/build_enhanced.sh
chmod +x build_enhanced.sh
./build_enhanced.sh --clean
```

### Option 2: Manual Build
```bash
# 1. Create directory
mkdir -p ~/mcp_cm_v1 && cd ~/mcp_cm_v1

# 2. Copy the essential files:
#    - mcp_fastmcp_server_extended.py
#    - catalog_manager_extended.py (or catalog_manager_extended_fixed.py)
#    - init_db_extended.sql
#    - requirements_*.txt files
#    - Dockerfile.*.enhanced files
#    - docker-compose.extended.yml

# 3. Build and deploy
docker-compose -f docker-compose.extended.yml build --no-cache
docker-compose -f docker-compose.extended.yml up -d

# 4. Verify
sleep 20
python3 verify_13_tools.py
```

## 🔌 Integration with Claude Desktop

Add to Claude Desktop configuration:
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "telepath-enhanced": {
      "url": "http://localhost:8090"
    }
  }
}
```

Restart Claude Desktop to see all 13 tools available.

## 📊 API Endpoints

### Catalog Manager (Port 8080)

#### TMF Forum APIs
- `POST /tmf637/serviceQualification` - Check service availability
- `GET /tmf629/customer/{id}` - Get customer information
- `POST /tmf622/productOrder` - Create product order
- `GET /tmf622/productOrder` - List orders
- `GET /tmf622/productOrder/{id}` - Get specific order
- `POST /tmf640/serviceActivation` - Activate service

#### Catalog Management APIs
- `GET/POST /api/service-specifications` - Manage service specs
- `GET/POST /api/product-offerings` - Manage product offerings
- `GET/POST /api/geographic-locations` - Manage locations
- `POST /api/sync-catalog-data` - Sync catalog
- `POST /api/link-offering-to-specification` - Link products to services
- `POST /api/add-geographic-coverage` - Add coverage areas
- `GET /api/catalog-integrity` - Check catalog integrity

### MCP Server (Port 8090)
- `POST /mcp/stream` - MCP streaming endpoint (JSON-RPC)
- `GET /health` - Health check (if available)

## 📝 Demo Data

The system comes pre-loaded with comprehensive demo data:

### Customers (6 total)
- CUST001-006: Jane Doe, John Smith, Alice Johnson, Bob Williams, Carol Brown, David Lee
- Various credit scores and account statuses

### Service Specifications
- Fiber Internet (100Mbps, 500Mbps, 1Gbps)
- Cable TV packages
- Mobile services (4G, 5G)
- VoIP services

### Product Offerings
- Internet plans ($49.99-$149.99/month)
- TV packages ($39.99-$89.99/month)
- Bundle packages ($89.99-$199.99/month)

### Geographic Coverage
- Springfield (Main St, Oak Ave, Elm St, Pine Rd, Maple Dr)
- Shelbyville (Cherry Ln)
- Various service types and speeds per location

## 🧪 Testing

### Run Verification Tests
```bash
# Install test dependencies
pip3 install -r requirements_test.txt

# Run comprehensive verification
python3 verify_13_tools.py

# Test individual endpoints
make -f Makefile.enhanced13 test

# Run demo
make -f Makefile.enhanced13 demo
```

### Manual Testing with curl
```bash
# Test service qualification
curl -X POST http://localhost:8090/mcp/stream \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "service_qualification",
      "arguments": {
        "address": {"streetName": "Main Street", "city": "Springfield"},
        "serviceSpecification": {"id": "fiber-100", "name": "Fiber 100Mbps"}
      }
    },
    "id": 1
  }'
```

## 🛠️ Development

### Useful Commands
```bash
# View logs
docker-compose -f docker-compose.extended.yml logs -f

# Database shell
docker exec -it telecom_postgres psql -U telecom_user -d telecom_catalog

# Container shells
docker exec -it catalog_manager /bin/bash
docker exec -it mcp_server /bin/bash

# Restart services
docker-compose -f docker-compose.extended.yml restart

# Clean rebuild
docker-compose -f docker-compose.extended.yml down -v
docker-compose -f docker-compose.extended.yml build --no-cache
docker-compose -f docker-compose.extended.yml up -d
```

### Project Structure
```
mcp_cm_v1/
├── Python Core Files
│   ├── mcp_fastmcp_server_extended.py    # 13-tool MCP server
│   ├── catalog_manager_extended.py       # Enhanced catalog API
│   └── verify_13_tools.py               # Verification script
│
├── Docker Configuration
│   ├── Dockerfile.catalog.enhanced      # Catalog container
│   ├── Dockerfile.mcp.enhanced         # MCP container
│   └── docker-compose.extended.yml     # Orchestration
│
├── Database
│   └── init_db_extended.sql           # Schema & sample data
│
├── Build Scripts
│   ├── Makefile.enhanced13            # Enhanced Makefile
│   ├── build_enhanced.sh              # Build script
│   └── fix_13_tools_now.sh           # Quick fix script
│
└── Documentation
    ├── README.md                      # This file
    ├── ENHANCED_BUILD_GUIDE.md        # Detailed build guide
    └── TROUBLESHOOTING.md             # Common issues
```

## 🐛 Troubleshooting

### Common Issues

1. **"No module named 'requests'" error**
   ```bash
   pip3 install requests
   ```

2. **API returns HTML instead of JSON**
   ```bash
   # Run the fix script
   ./fix_13_tools_now.sh
   ```

3. **Port already in use**
   ```bash
   # Find and kill process
   sudo lsof -i :8080
   sudo lsof -i :8090
   ```

4. **Docker permission denied**
   ```bash
   sudo usermod -aG docker $USER
   newgrp docker
   ```

5. **Services not starting**
   ```bash
   # Check logs
   docker-compose -f docker-compose.extended.yml logs catalog-manager
   docker-compose -f docker-compose.extended.yml logs mcp-server
   ```

## 🔒 Security Considerations

**⚠️ This is a demo system** with:
- No authentication/authorization
- Hardcoded passwords
- Open network ports
- Sample data only

**For production**, implement:
- OAuth2/JWT authentication
- TLS/SSL encryption
- Network segmentation
- Secrets management (Vault, KMS)
- Rate limiting
- Input validation
- RBAC (Role-Based Access Control)

## 📈 Performance

- Supports concurrent requests
- Database connection pooling
- Async operations in MCP server
- Docker resource limits configurable
- Typical response time: <100ms

## 🚦 Next Steps

1. ✅ ~~Expand from 4 to 13 tools~~ (Completed in v2.0)
2. Add remaining TM Forum APIs (TMF620, TMF633, TMF634)
3. Implement authentication and authorization
4. Add real network activation interfaces
5. Implement monitoring (Prometheus/Grafana)
6. Add CI/CD pipeline
7. Performance optimization and caching
8. Multi-tenant support
9. Event-driven architecture with Kafka
10. GraphQL API layer

## 📄 License

This is a demonstration project for the Telepath AI initiative.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📞 Support

For issues and questions:
- Check [TROUBLESHOOTING.md](./TROUBLESHOOTING.md)
- Review [ENHANCED_BUILD_GUIDE.md](./ENHANCED_BUILD_GUIDE.md)
- Open an issue on GitHub

---

**Version**: 2.0.0  
**Last Updated**: December 2024  
**Status**: Production Ready (Demo)  
**Tools**: 13 MCP Tools Available
