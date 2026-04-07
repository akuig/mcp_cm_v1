# Architecture

**Analysis Date:** 2026-04-07

## Pattern Overview

**Overall:** Two-tier distributed MCP architecture with HTTP REST API bridge and HTTP streaming MCP server.

**Key Characteristics:**
- REST API layer (FastAPI/Flask) decouples business logic from MCP protocol
- HTTP streaming transport (not stdio) for Claude Desktop compatibility
- Dual database access: REST layer (psycopg2) and MCP layer (aiohttp client to REST)
- TMF Forum compliance (TMF622, TMF629, TMF637, TMF640)
- Async/await pattern with aiohttp for MCP server HTTP calls
- Audit logging on every tool invocation for compliance

## Layers

**REST API Layer (Catalog Manager):**
- Purpose: Provide TM Forum-compliant endpoints for catalog, customer, order, and activation operations
- Location: `catalog_manager_extended.py` (production), `catalog_manager.py` (simplified in-memory version)
- Contains: Flask routes, database cursor management, TMF endpoint handlers
- Depends on: PostgreSQL (psycopg2 connection), request/response JSON handling
- Used by: MCP server (via aiohttp HTTP client)

**MCP Server Layer:**
- Purpose: Expose catalog manager REST APIs as MCP tools/resources for Claude Desktop
- Location: `mcp_fastmcp_server_extended.py` (production), `mcp_fastmcp_server.py` (simpler version)
- Contains: FastMCP decorated tools, resource handlers, audit logging
- Depends on: Catalog manager REST endpoints, aiohttp for HTTP calls
- Used by: Claude Desktop via HTTP streaming on port 8090

**Database Layer:**
- Purpose: Persist catalog, customer, order, and coverage data
- Location: PostgreSQL 15 (container), initialized by `init_db.sql` or `init_db_extended.sql`
- Contains: service_specifications, customers, orders, service_coverage, service_activations tables
- Depends on: Schema DDL and seed data from SQL scripts

## Data Flow

**Service Qualification Flow (TMF637):**
1. Client calls MCP tool `service_qualification` with address and service spec
2. MCP server (aiohttp) POSTs to catalog manager REST endpoint `/tmf637/serviceQualification`
3. Catalog manager queries service_specifications table by service ID
4. Catalog manager queries service_coverage table by street_name, city, service_type
5. Returns qualification result (qualified/unqualified) with estimated provisioning date
6. Audit entry logged with timestamp, correlationId, request, response, status

**Product Order Creation Flow (TMF622):**
1. Client calls MCP tool `product_ordering` with orderDate, customerId, productOfferingId, address
2. MCP server transforms to TMF622 format and POSTs to `/tmf622/productOrder`
3. Catalog manager validates customer exists, product offering exists
4. Inserts order record in orders table with status='acknowledged'
5. Creates order_address record with delivery location
6. Returns created order with ID and status
7. Audit entry logged

**Service Activation Flow (TMF640):**
1. Client calls MCP tool `service_activation` with serviceName, serviceType, address, serviceSpecificationId
2. MCP server transforms to TMF640 format and POSTs to `/tmf640/serviceActivation`
3. Catalog manager inserts service_activations record with status='active'
4. Creates activation_address record
5. Returns activation confirmation with timestamp
6. Audit entry logged

**State Management:**
- In-memory for development: Python lists in catalog_manager.py (re-initialized on restart)
- Persistent for production: PostgreSQL tables via psycopg2 connections
- MCP state: aiohttp session created on first tool call, reused across calls, cleaned up on shutdown
- Order states: acknowledged → inProgress → pending → held → completed (or cancelled/failed/rejected)

## Key Abstractions

**TMF Forum Endpoint Handler:**
- Purpose: Map HTTP REST routes to TM Forum standard payloads
- Examples: `/tmf637/serviceQualification`, `/tmf629/customer/{id}`, `/tmf622/productOrder`, `/tmf640/serviceActivation`
- Pattern: Route handler receives request.json, queries database, returns jsonify(result)
- Validation: Database lookups to ensure referenced entities exist before returning success

**MCP Tool Wrapper:**
- Purpose: Provide async interface for Claude Desktop while calling HTTP endpoints
- Examples: `service_qualification()`, `product_ordering()`, `order_management()`
- Pattern: @mcp.tool() decorator, async def, await session.post/get, log_audit(), raise Exception on error
- Response format: Dict[str, Any] with payload structure matching TMF standard

**MCP Resource (Read-only):**
- Purpose: Provide browsable data catalog without requiring tool parameters
- Examples: `customers://list`, `services://catalog`, `orders://recent`
- Pattern: @mcp.resource() decorator, async def, return JSON string
- Use case: Answer questions like "show me all customers" without Claude guessing parameters

**Database Connection Pool:**
- Purpose: Manage psycopg2 connections to PostgreSQL
- Pattern: get_db_connection() function creates new cursor_factory=RealDictCursor connection per request
- Why RealDictCursor: Returns rows as dicts (cursor.fetchone()['column_name']) instead of tuples
- Cleanup: cursor.close(), conn.close() in finally blocks to avoid connection leaks

**Audit Logger:**
- Purpose: Track all MCP tool invocations for compliance
- Pattern: log_audit(action, request, response) called after every tool success or failure
- Format: JSON with timestamp (ISO 8601 UTC), correlationId, action name, request payload, response payload, status
- Output: logger.info() writes to stderr/logs

## Entry Points

**REST API Entry Point:**
- Location: `catalog_manager_extended.py` main function at module level (or catalog_manager.py)
- Triggers: Docker container startup via CMD ["python", "-u", "catalog_manager.py"]
- Responsibilities: Initialize Flask app, load database config from env vars, start HTTP server on port 8080
- Routes exposed: /health, /tmf637/*, /tmf629/*, /tmf622/*, /tmf640/*, /api/*

**MCP Server Entry Point:**
- Location: `mcp_fastmcp_server_extended.py` module level (FastMCP instance creation)
- Triggers: Docker container startup via CMD ["fastmcp", "run", "..."] or direct python execution
- Responsibilities: Create FastMCP server on port 8090, register tools/resources, start event loop, handle HTTP streaming
- Protocol: HTTP streaming (not stdio) - Claude Desktop connects via /mcp endpoint at port 8090

**Database Initialization:**
- Location: `init_db_extended.sql` or `init_db.sql`
- Triggers: Docker postgres container entrypoint, executes /docker-entrypoint-initdb.d/init_db.sql on first start
- Responsibilities: Create tables (service_specifications, customers, orders, service_coverage, service_activations, etc.), insert demo data
- Idempotency: Uses CREATE TABLE IF NOT EXISTS and INSERT ... ON CONFLICT (if applicable)

## Error Handling

**Strategy:** Try-catch with jsonify error responses; MCP tools raise Exception with descriptive message.

**Patterns:**
- REST layer: try/except in route handlers, return jsonify({"error": message}), 500 or 404 status codes
- MCP layer: try/except around async session calls, log_audit() on error, raise Exception(f"Action failed: {str(e)}")
- Database errors: Catch psycopg2.Error, return 500 with generic "Database error" to avoid leaking schema details
- HTTP timeouts: DEFAULT_TIMEOUT = 30 seconds (configurable), logged as connection error if exceeded

## Cross-Cutting Concerns

**Logging:** Python logging module, basicConfig(level=logging.INFO), logger = logging.getLogger(__name__), log_audit() for compliance

**Validation:** Minimal validation in REST layer (assume requests well-formed); MCP layer does not validate (trusts Claude Desktop)
- TMF622 order creation: Validates customer_id exists, product_offering_id exists before inserting order
- TMF629 customer lookup: Returns 404 if customer not found
- No input type checking in MCP tool signatures (Zod/pydantic not used)

**Authentication:** None implemented. Assumes local Docker network (mcp-server → catalog-manager via internal network). Production would require API key or JWT bearer token.

**Database Transactions:** Implicit PostgreSQL autocommit (no explicit BEGIN/COMMIT). Single-statement queries. No rollback on error - database may be left in inconsistent state if query fails midway (risk for production).

---

*Architecture analysis: 2026-04-07*
