# Telepath AI Demo System

A demonstration system for the Telepath AI project that exposes telecommunications BSS/OSS systems through Model Context Protocol (MCP) servers, enabling autonomous operation by AI agents.

## Overview

This MVP focuses on the Catalog Manager system, implementing:
- MCP Server using FastMCP with HTTP streaming transport (compatible with Claude Desktop)
- Mock Catalog Manager implementing the TM Forum APIs
- PostgreSQL database with demo customer and service data
- Complete Docker-based deployment

## Key Features

- **HTTP Streaming Transport**: The server uses FastMCP's streamable-http transport, allowing it to work with both Claude Desktop and remote deployments
- **TM Forum API Integration**: Wraps TMF622, TMF629, TMF637, and TMF640 APIs
- **Full Audit Logging**: All operations are logged for compliance
- **Docker Deployment**: Easy deployment with docker-compose

## Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   AI Agent      │────▶│   MCP Server    │────▶│ Catalog Manager │
│ (MCP Client)    │HTTP │   (Port 8090)   │ HTTP│  (TM Forum APIs)│
└─────────────────┘Stream└─────────────────┘     └────────┬────────┘
                                                          │
                                                          ▼
                                                 ┌─────────────────┐
                                                 │   PostgreSQL    │
                                                 │    Database     │
                                                 └─────────────────┘
```

The MCP Server uses HTTP streaming (chunked transfer encoding) for real-time communication.

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Python 3.8+ with pip
- Node.js (optional, for MCP Inspector)
- curl and jq (for testing)

### Installation & Running

1. Clone the repository and navigate to the project directory

2. Run the setup script:
```bash
chmod +x setup.sh
./setup.sh
```

3. Build and start all services:
```bash
make build
make up
```

4. Verify services are running:
```bash
make health
```

5. Run automated tests:
```bash
make test-mcp
```

### Alternative: Using Python Virtual Environment

For isolated testing:
```bash
# Create virtual environment
make venv

# Activate it
source venv/bin/activate

# Install dependencies
pip install -r requirements_test.txt

# Run tests
python test_mcp.py
```

### Using MCP with HTTP Streaming

The MCP server uses FastMCP with HTTP streaming transport for real-time communication.

#### Option 1: Using Claude Desktop

Add to Claude Desktop configuration:
- On macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- On Windows: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "telepath-mcp": {
      "url": "http://localhost:8090"
    }
  }
}
```

Restart Claude Desktop and you'll see "telepath-mcp" in the servers list.

#### Option 2: Using MCP Inspector

```bash
# The server works directly with MCP Inspector
make inspector
```

#### Option 3: Direct HTTP Testing

```bash
# Test with curl
curl -X POST http://localhost:8090/mcp/stream \
  -H "Content-Type: application/json" \
  -H "Accept: application/json-stream" \
  -d '{"jsonrpc": "2.0", "method": "tools/list", "params": {}, "id": 1}'
```

### MCP Server Endpoints

The MCP server uses HTTP streaming transport with the following endpoints:
- **Streaming endpoint**: `http://localhost:8090/mcp/stream` - For MCP client connections (chunked HTTP)
- **Legacy endpoint**: `http://localhost:8090/messages` - For compatibility
- **Health check**: `http://localhost:8090/health` - Service health status

## Available MCP Tools

### 1. service_qualification
Check if a service is available at a specific location (TMF637)

### 2. customer_management
Get customer information including account status and eligibility (TMF629)

### 3. product_ordering
Create a product order for a customer (TMF622)

### 4. service_activation
Activate a service in the network (TMF640)

## Demo Data

The system comes pre-loaded with:

**Customers:**
- Jane Doe (8452934) - Good credit, active account
- John Smith (8452935) - Has overdue payments
- Alice Johnson (8452936) - Excellent credit
- Bob Williams (8452937) - Suspended account

**Service Coverage:**
- Main Street, Springfield - Fiber (1000 Mbps)
- Oak Avenue, Springfield - Fiber (1000 Mbps)
- Elm Street, Springfield - Cable (200 Mbps)
- Pine Road, Springfield - DSL (50 Mbps)
- Cherry Lane, Shelbyville - Cable (100 Mbps)

## API Endpoints

The Catalog Manager exposes the following endpoints:

- `POST /tmf637/serviceQualification` - Check service availability
- `GET /tmf629/customer/{id}` - Get customer information
- `POST /tmf622/productOrder` - Create product order
- `POST /tmf640/serviceActivation` - Activate service

## Development

### Project Structure
```
.
├── mcp_server.py           # MCP Server implementation
├── catalog_manager.py      # Mock Catalog Manager (TM Forum APIs)
├── init_db.sql            # Database schema and demo data
├── docker-compose.yml     # Container orchestration
├── Dockerfile.mcp         # MCP Server container
├── Dockerfile.catalog     # Catalog Manager container
├── requirements_*.txt     # Python dependencies
├── test_mcp.py           # Automated test script
├── test_scenarios.md     # Manual test scenarios
├── Makefile              # Build and run commands
└── README.md             # This file
```

### Useful Commands

```bash
# View logs
make logs

# Connect to database
make db-shell

# Stop all services
make down

# Clean everything
make clean

# Run concurrent tests
python test_mcp.py --concurrent 10
```

## Security Considerations

This is a demo system with:
- No authentication/authorization
- Hardcoded passwords
- Open network ports

For production use, implement:
- Proper authentication (OAuth2/JWT)
- TLS/SSL encryption
- Network segmentation
- Secrets management
- Rate limiting
- Input validation

## Next Steps

1. Implement remaining TM Forum APIs (TMF620, TMF633, TMF634)
2. Add authentication and authorization
3. Implement real network activation interfaces
4. Add monitoring and alerting (Prometheus/Grafana)
5. Implement CI/CD pipeline
6. Add more comprehensive error handling
7. Performance optimization and caching

## License

This is a demonstration project for the Telepath AI initiative.
