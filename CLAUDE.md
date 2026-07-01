# CLAUDE.md — Telepath AI MCP Orchestration Platform

## Project Overview

Telepath AI is an MCP (Model Context Protocol) orchestration platform for telecommunications. It enables AI agents to interact with traditionally siloed BSS (Business Support Systems) and OSS (Operations Support Systems) through TM Forum-standard APIs. The core value proposition: MCP completes existing RAG/LLM investments by adding real-time operational data and the ability to ACT on systems, not just query knowledge bases.

**Company:** akuig / Telepath AI
**Founder:** Joe (40+ years telecoms experience, founded Aldiscon and Ammeon)
**Project root:** `/Users/joe/dev/mcp_cm_v1`

## Architecture

The platform consists of two independent MCP servers that connect to separate databases, realistically representing how BSS and OSS systems operate independently in actual telecom environments. Integration between them happens through customer ID references, not shared databases.

### System Components

| Component | Port | Database | Purpose |
|-----------|------|----------|---------|
| **BSS Catalogue Manager** | 8080 | PostgreSQL (port 5432, db: `telecom_catalog`, user: `telecom_user`) | Customer management, product catalog, orders, service activation |
| **ENM Simulator** | 8081 (API), 8082 (MCP) | PostgreSQL (port 5433, db: `enm_sim`, user: `enm`) + Redis (port 6380) | Network element management, alarms, topology, fault management |

### Key Files

- `src/catalog_manager_enhanced.py` → Main BSS catalog manager (runs as `catalog_manager.py` in container)
- `mcp_fastmcp_server_extended.py` → BSS MCP server exposing TMF tools
- ENM simulator lives at `/Users/joe/dev/enm_sim`
- Working HTTP streaming reference server: `/Users/joe/dev/working_server/server.py`

### Build & Run

```bash
# Start BSS
cd /Users/joe/dev/mcp_cm_v1
docker-compose up -d

# Health check
curl http://localhost:8080/health

# ENM (separate project directory)
cd /Users/joe/dev/enm_sim
docker-compose up -d
curl -X POST http://localhost:8081/admin/seed   # Seed network data
```

### Claude Desktop Configuration

Uses HTTP streaming (NOT stdio). Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "catalog-manager": {
      "url": "http://localhost:8080/mcp",
      "name": "Catalog Manager"
    },
    "enm-simulator": {
      "url": "http://localhost:8082/mcp",
      "name": "ENM Simulator"
    }
  }
}
```

**Critical:** Claude Desktop requires HTTP streaming transport (`transport="streamable-http"` in FastMCP), not stdio. This was a hard-won lesson — many iterations of trying stdio bridges before landing on direct HTTP streaming.

## TM Forum APIs Implemented

### BSS Catalogue Manager (20+ tools)

**TMF Standard APIs:**

| Tool | TMF Standard | Description |
|------|-------------|-------------|
| `service_qualification` | TMF637 | Check service availability at a location |
| `customer_management` | TMF629 | Get customer info, account status, eligibility |
| `create_customer` | TMF629 | Create new customer |
| `update_customer` | TMF629 | Update existing customer (PATCH semantics) |
| `delete_customer` | TMF629 | Delete customer (fails if linked orders exist) |
| `product_ordering` | TMF622 | Create product orders |
| `order_management` | TMF622 | List/retrieve/filter orders |
| `cancel_order` | TMF622 | Cancel an order |
| `delete_order` | TMF622 | Permanently remove an order |
| `update_order_status` | TMF622 | Change order state (acknowledged, inProgress, pending, held, completed, cancelled, failed, rejected) |
| `service_activation` | TMF640 | Activate services in the network |

**Catalog Management Tools:**

| Tool | Description |
|------|-------------|
| `list_service_specifications` | List/filter service specs |
| `list_product_offerings` | List/filter product offerings with pricing |
| `list_geographic_locations` | List locations with coverage info |
| `sync_catalog_data` | Validate and sync catalog integrity |
| `create_service_specification` | Create new service specs |
| `create_product_offering` | Create new product offerings |
| `link_offering_to_specification` | Link products to services |
| `add_geographic_coverage` | Add coverage areas |

### ENM Network Manager (18 tools)

| Tool | Description |
|------|-------------|
| `enm_get_network_element` | Get NE by ID |
| `enm_list_network_elements` | List/filter NEs by type, site, state |
| `enm_get_topology_tree` | Hierarchical parent-child view |
| `enm_get_topology_overview` | Network summary with counts |
| `enm_get_connections` | List connections (fiber, ethernet, microwave, coax) |
| `enm_get_network_path` | Path between two elements |
| `enm_get_alarms` | Get alarms with filtering |
| `enm_get_alarm_summary` | Alarm counts by severity |
| `enm_acknowledge_alarm` | Acknowledge an alarm |
| `enm_clear_alarm` | Clear/resolve an alarm |
| `enm_get_alarm_impact` | Customer impact of an alarm |
| `enm_find_root_cause` | Root cause analysis |
| `enm_get_customers_by_element` | Customers served by a NE |
| `enm_get_customer_equipment` | CPE for a customer ID (links BSS↔OSS) |
| `enm_get_impact_analysis` | What-if failure analysis |
| `enm_get_pm_data` | Performance metrics |
| `enm_inject_fault` | Create test alarm (for demos) |
| `enm_update_element_state` | Lock/unlock NE |

## Test Data & Demo Environment

### Test Customers (BSS)

| ID | Name | Status | City | Address | Credit | Overdue |
|----|------|--------|------|---------|--------|---------|
| 8452934 | Jane Doe | Active | Springfield | 456 Main Street | 720 | No |
| 8452935 | John Smith | Active | Springfield | 123 Main Street | 650 | Yes |
| 8452936 | Alice Johnson | Active | Springfield | 789 Oak Avenue | 780 | No |
| 8452937 | Bob Williams | Suspended | Springfield | 321 Elm Street | 550 | Yes |
| 8452938 | Carol Brown | Active | Springfield | 555 Maple Drive | 695 | No |
| 8452939 | David Lee | Active | Shelbyville | 777 Cherry Lane | 640 | No |

### Network Topology (ENM)

The network covers Springfield and Shelbyville with a realistic multi-technology hierarchy:

- **Core Router** → OLTs (fiber), CMTS (cable), eNodeBs (LTE), gNodeBs (5G)
- **Springfield:** SPFLD-OLT-01, SPFLD-OLT-02, SPFLD-CMTS-01, SPFLD-ENB-01, SPFLD-GNB-01
- **Shelbyville:** SHBY-OLT-01, SHBY-CMTS-01
- **CPE:** ONT-{customerID} for fiber customers, CM-{customerID} for cable customers
- Connections: fiber, ethernet, microwave, coax between elements

### Key Demo Scenarios

1. **End-to-end service provisioning:** Qualify → Order → Activate for a customer
2. **Fault injection & impact analysis:** `enm_inject_fault` on SPFLD-OLT-01 → identify impacted customers → correlate with SLA tiers
3. **Cross-silo orchestration:** Network fault detected in ENM → AI identifies affected BSS customers → prioritizes by SLA
4. **Order lifecycle:** Create, update status, cancel, delete orders for demo reset

## Coding Conventions

- **Python 3.11+** throughout
- **FastMCP** for MCP server implementation (not raw MCP SDK)
- **FastAPI** for REST APIs in catalog manager
- **PostgreSQL 15** for databases
- **Docker Compose** for local development and deployment
- **TMF Forum compliance** — API payloads follow TMF622, TMF629, TMF637, TMF640 schemas
- API responses must handle both list and dict formats (a recurring source of bugs)
- Audit logging on every MCP tool call (timestamp, correlationId, action, request, response, status)
- Use `--break-system-packages` flag when pip installing in containers

## Common Pitfalls

1. **HTTP streaming, not stdio** — Claude Desktop connects via `url` field in config, not `command`/`args`. Use `transport="streamable-http"` in FastMCP.
2. **Separate databases** — BSS and ENM use different PostgreSQL instances. Don't assume shared tables.
3. **TMF response format** — Some TMF endpoints return lists, others return dicts. Always handle both.
4. **Customer ID linkage** — The bridge between BSS and ENM is the customer ID (e.g., 8452934). ENM's `enm_get_customer_equipment` maps customer IDs to network CPE devices.
5. **Database schema sync** — Schema in `init_db.sql` must match what the Python code expects. After schema changes, recreate the database volume: `docker-compose down -v && docker-compose up -d`.
6. **ENM connects to BSS** — ENM simulator has `CATALOG_MANAGER_URL=http://host.docker.internal:8080` to reference BSS customers.

## Business Context

- **Target customers:** Major carriers (Telenor, Telia, Singtel)
- **Positioning:** MCP completes RAG investments — RAG provides historical knowledge, MCP provides real-time operational data and actions
- **Key differentiators:** TMF standards compliance, full audit trail, cross-silo orchestration, progressive risk mitigation
- **Deployment methodology:** "Start Small → Scale with Confidence" — read-only intelligence → assisted operations → autonomous operations → business intelligence
- **Audit trail** is a killer differentiator that addresses enterprise governance concerns
