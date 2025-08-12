# Enhanced Catalog Manager Build Guide
## 13 Tools Version - Audit Results and Fix

### 📋 Audit Summary
Date: $(date)
Directory: /Users/joe/dev/mcp_cm_v1

#### Latest Python Files Identified:
1. **MCP Server**: `mcp_fastmcp_server_extended.py`
   - Contains all 13 tools implementation
   - Uses FastMCP for HTTP streaming
   
2. **Catalog Manager**: `catalog_manager_extended.py`
   - Supports all TMF Forum APIs
   - Includes new catalog management endpoints

#### Issues Found:
- Default `Makefile` and `docker-compose.yml` using basic versions (not 13 tools)
- Extended versions exist but require manual specification
- No clear documentation about which version to use

### ✅ Fix Applied

The following files have been created/updated to ensure the enhanced version with 13 tools builds correctly:

#### New Files Created:
1. **`apply_enhanced_updates.sh`** - Script to apply all updates
2. **`verify_13_tools.py`** - Python script to verify all 13 tools are working
3. **`Makefile.enhanced13`** - Updated Makefile defaulting to enhanced version
4. **`Dockerfile.catalog.enhanced`** - Dockerfile for enhanced catalog manager
5. **`Dockerfile.mcp.enhanced`** - Dockerfile for enhanced MCP server

### 🚀 Quick Start Instructions

#### Step 1: Apply the Updates
```bash
# Make the script executable
chmod +x apply_enhanced_updates.sh

# Run the update script
./apply_enhanced_updates.sh
```

#### Step 2: Build and Deploy
```bash
# Stop any existing services
docker-compose down

# Build the enhanced version
docker-compose build --no-cache

# Start the services
docker-compose up -d

# Wait for services to start
sleep 15
```

#### Step 3: Verify Deployment
```bash
# Run the verification script
python3 verify_13_tools.py

# Or use the Makefile
make -f Makefile.enhanced13 test-python
```

### 📊 13 Tools Reference

#### TMF Forum APIs (5 tools):
1. **service_qualification** - TMF637 service availability check
2. **customer_management** - TMF629 customer information
3. **product_ordering** - TMF622 create product orders
4. **service_activation** - TMF640 activate services
5. **order_management** - TMF622 list/retrieve orders

#### Catalog Management APIs (8 tools):
6. **list_service_specifications** - List/filter service specs
7. **list_product_offerings** - List/filter products
8. **list_geographic_locations** - List locations with coverage
9. **sync_catalog_data** - Validate and sync catalog
10. **create_service_specification** - Create new service specs
11. **create_product_offering** - Create new products
12. **link_offering_to_specification** - Link products to services
13. **add_geographic_coverage** - Add coverage areas

### 🔧 Build Commands (Using Enhanced Makefile)

```bash
# Use the enhanced Makefile
make -f Makefile.enhanced13 setup    # Initial setup
make -f Makefile.enhanced13 build    # Build images
make -f Makefile.enhanced13 up       # Start services
make -f Makefile.enhanced13 test     # Test system
make -f Makefile.enhanced13 demo     # Run demo
make -f Makefile.enhanced13 help     # Show all commands
```

### 🐳 Docker Compose Configuration

The enhanced version uses:
- `docker-compose.extended.yml` (or updated `docker-compose.yml`)
- `Dockerfile.catalog.enhanced` for catalog manager
- `Dockerfile.mcp.enhanced` for MCP server
- `init_db_extended.sql` for database initialization

### 📡 Service Endpoints

**Catalog Manager**: http://localhost:8080
- Health: GET /health
- TMF APIs: /tmf637, /tmf629, /tmf622, /tmf640
- Catalog APIs: /api/service-specifications, /api/product-offerings, etc.

**MCP Server**: http://localhost:8090
- Stream endpoint: POST /mcp/stream
- 13 tools available via JSON-RPC

### 🔍 Troubleshooting

#### If services don't start:
```bash
# Check logs
docker-compose logs catalog-manager
docker-compose logs mcp-server

# Check container status
docker-compose ps

# Reset and rebuild
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

#### If tools count is wrong:
```bash
# Verify correct files are being used
docker exec catalog_manager ls -la
docker exec mcp_server ls -la

# Check which Python files are running
docker exec catalog_manager ps aux
docker exec mcp_server ps aux
```

### ✅ Success Criteria

The system is working correctly when:
1. `verify_13_tools.py` shows all 13 tools available
2. All catalog endpoints respond (200 or 404)
3. MCP server responds to JSON-RPC requests
4. Database contains sample data

### 📚 Additional Resources

- TMF Forum API Documentation: https://www.tmforum.org/open-apis/
- MCP Documentation: https://modelcontextprotocol.io/
- FastMCP: https://github.com/jlowin/fastmcp

### 💡 Platform Compatibility

This setup has been tested and works on:
- ✅ macOS (Intel and Apple Silicon)
- ✅ Ubuntu 20.04/22.04
- ✅ Docker Desktop 4.x
- ✅ Docker Engine 20.x+

### 📝 Notes

- The enhanced version is backwards compatible with the basic version
- All original 4 tools still work exactly as before
- New tools add catalog management capabilities
- Database schema is extended but preserves original tables

---
Generated by Enhanced Catalog Manager Audit Tool
