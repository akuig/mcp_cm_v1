# Fault Management Extension for Telepath AI Demo

## Overview

This extension adds comprehensive fault management capabilities to the Telepath AI demo, showcasing how telecom operators can handle network issues efficiently using AI agents.

## New Components

### 1. Fault Manager Service (`fault_manager.py`)
- Implements TMF656 (Service Problem Management) and TMF621 (Trouble Ticket Management)
- Simulates network faults (fiber cut on Main Street)
- Provides remedial action execution

### 2. Enhanced MCP Server (`mcp_fastmcp_server_with_fault.py`)
New tools exposed:
- `check_service_status` - Real-time service health monitoring
- `create_trouble_ticket` - Customer issue tracking
- `execute_remedial_action` - Automated recovery actions
- `get_service_problems` - Area-wide problem visibility

### 3. Test Script (`test_fault_management.py`)
Demonstrates the complete fault management scenario

## Quick Start

1. **Make the setup script executable:**
```bash
chmod +x setup_fault_management.sh
```

2. **Run the setup:**
```bash
./setup_fault_management.sh
```

3. **Test the fault scenario:**
```bash
python test_fault_management.py
```

## Demo Scenario

1. **Initial State**: Jane Doe has active Premium Fiber service
2. **Fault Occurs**: Fiber cut on Main Street affects 150 customers
3. **Customer Call**: Jane reports service disruption
4. **AI Agent Actions**:
   - Checks service status
   - Identifies network fault
   - Reroutes traffic (15-minute restoration)
   - Dispatches technician (4-hour permanent fix)
   - Creates trouble ticket
   - Notifies affected customers

## Using with Claude Desktop

Update your Claude Desktop configuration to use the fault-enabled MCP server:

```json
{
  "mcpServers": {
    "telepath-mcp": {
      "command": "docker",
      "args": [
        "run",
        "--rm",
        "--network", "host",
        "telepath-mcp-fault:latest"
      ]
    }
  }
}
```

## Available Endpoints

- Catalog Manager: http://localhost:8080
- Fault Manager API: http://localhost:8081/docs
- MCP Server: http://localhost:8090

## Docker Commands

```bash
# Start services
docker-compose -f docker-compose-with-fault.yml up -d

# View logs
docker-compose -f docker-compose-with-fault.yml logs -f

# Stop services
docker-compose -f docker-compose-with-fault.yml down

# Rebuild after changes
docker-compose -f docker-compose-with-fault.yml build
```

## Testing Individual Components

### Test Fault Manager directly:
```bash
# Check service status
curl -X POST http://localhost:8081/serviceStatus/check \
  -H "Content-Type: application/json" \
  -d '{"location": {"streetName": "Main Street", "city": "Dublin"}}'

# Execute remedial action
curl -X POST http://localhost:8081/serviceStatus/executeAction \
  -H "Content-Type: application/json" \
  -d '{"action": "REROUTE_TRAFFIC"}'
```

### Test MCP Tools:
```bash
# Check service status via MCP
curl -X POST http://localhost:8090/tools/check_service_status \
  -H "Content-Type: application/json" \
  -d '{"location": {"streetName": "Main Street", "streetNumber": "123", "city": "Dublin"}}'
```

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Claude Agent   │────▶│   MCP Server     │────▶│ Fault Manager   │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                               │                           │
                               │                           │
                               ▼                           ▼
                        ┌──────────────────┐      ┌─────────────────┐
                        │ Catalog Manager  │      │ Network Faults  │
                        └──────────────────┘      │ Trouble Tickets │
                               │                  │ Service Problems│
                               ▼                  └─────────────────┘
                        ┌──────────────────┐
                        │   PostgreSQL     │
                        └──────────────────┘
```

## Troubleshooting

1. **Port conflicts**: Ensure ports 8080, 8081, 8090, and 5432 are available
2. **Container issues**: Check logs with `docker-compose -f docker-compose-with-fault.yml logs [service-name]`
3. **Database issues**: Reset with `docker-compose -f docker-compose-with-fault.yml down -v`
