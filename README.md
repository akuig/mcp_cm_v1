# Telepath AI Demo System

A demonstration system for the Telepath AI project that exposes telecommunications BSS/OSS systems through Model Context Protocol (MCP) servers, enabling autonomous operation by AI agents.

## Overview

This MVP focuses on the Catalog Manager system, implementing:
- MCP Server wrapping TM Forum APIs (TMF622, TMF629, TMF637, TMF640)
- Mock Catalog Manager implementing the TM Forum APIs
- PostgreSQL database with demo customer and service data
- Complete Docker-based deployment

## Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   AI Agent      │────▶│   MCP Server    │────▶│ Catalog Manager │
│ (MCP Inspector) │ MCP │                 │ HTTP│  (TM Forum APIs)│
└─────────────────┘     └─────────────────┘     └────────┬────────┘
                                                          │
                                                          ▼
                                                 ┌─────────────────┐
                                                 │   PostgreSQL    │
                                                 │    Database     │
                                                 └─────────────────┘
```

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Python 3.11+
- Node.js (for MCP Inspector)

### Installation & Running

1. Clone the repository and navigate to the project directory

2. Build and start all services:
```bash
make build
make up
```

3. Verify services are running:
```bash
make health
```

4. Run automated tests:
```bash
python test_mcp.py
```

### Using MCP Inspector

1. Install MCP Inspector:
```bash
npm install -g @anthropic/mcp-inspector
```

2. Connect to the MCP server:
```bash
# In one terminal
docker exec -it mcp_server python mcp_server.py

# In another terminal
mcp-inspector
```

3. Follow the test scenarios in `test_scenarios.md`

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
