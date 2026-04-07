# External Integrations

**Analysis Date:** 2026-04-07

## APIs & External Services

**Internal Service Communication:**
- Catalog Manager REST API (`http://catalog-manager:8080`)
  - Used by: MCP server (`mcp_fastmcp_server_extended.py`)
  - Auth: None (internal Docker network communication)
  - Purpose: MCP tools invoke catalog manager endpoints to fulfill TMF API requests

## Data Storage

**Databases:**
- PostgreSQL 15 (Alpine)
  - Connection: `postgres://telecom_user:telecom_pass@postgres:5432/telecom_catalog`
  - Port: 5432 (exposed via Docker, configurable via `DB_PORT`)
  - Client: psycopg2-binary (Python PostgreSQL adapter)
  - Schema: `init_db_extended.sql` (defines customers, orders, service_specifications, product_offerings, geographic_locations, service_coverage, catalog_integrity tables)
  - Accessed by: `catalog_manager_extended.py` via `get_db_connection()` helper function

**File Storage:**
- Local filesystem only
  - Demo configuration: `config.yaml`
  - Logs directory: `/app/logs` (created in containers)
  - Persistent data: PostgreSQL volume (`postgres_data`)

**Caching:**
- None detected - all data reads hit PostgreSQL directly

## Authentication & Identity

**Auth Provider:**
- None - internal system without external identity provider
- Database credentials stored in environment variables (PostgreSQL user/password)
- No API token or bearer token authentication between services

## Monitoring & Observability

**Error Tracking:**
- None - no external error tracking service (Sentry, DataDog, etc.)

**Logs:**
- Structured JSON logging via `python-json-logger`
- Audit trail logged at every MCP tool invocation (timestamp, correlationId, action, request, response, status)
- Logging to stdout/stderr (captured by Docker)
- Log level configurable via Python logging (default: INFO)

## CI/CD & Deployment

**Hosting:**
- Docker Compose for local development
- No cloud platform integration detected
- Production deployment: Manual Docker Compose on remote server (via scp and ssh per `CLAUDE.md`)
- Remote server: `46.62.168.169` (user: `joe`)

**CI Pipeline:**
- None detected - manual build/deploy workflow

## Environment Configuration

**Required env vars:**
- `DB_HOST` - PostgreSQL hostname (default: `postgres`)
- `DB_PORT` - PostgreSQL port (default: `5432`)
- `DB_NAME` - PostgreSQL database name (default: `telecom_catalog`)
- `DB_USER` - PostgreSQL username (default: `telecom_user`)
- `DB_PASSWORD` - PostgreSQL password (default: `telecom_pass`)
- `CATALOG_MANAGER_URL` - Base URL for catalog manager (default: `http://catalog-manager:8080`)
- `PORT` - MCP server port (default: `8090`)
- `HOST` - MCP server bind address (default: `0.0.0.0`)

**Secrets location:**
- `.env` file (not committed to git) - PostgreSQL credentials
- Docker environment variables in `docker-compose.yml`
- Note: `.env` should never be committed; credentials are environment-scoped

## Webhooks & Callbacks

**Incoming:**
- None detected - API is stateless request/response

**Outgoing:**
- None detected - no external API calls to third-party services

## TMF Forum API Endpoints Exposed

The catalog manager exposes these RESTful endpoints implementing TM Forum standards:

**TMF637 (Service Qualification):**
- `POST /tmf637/serviceQualification` - Check service availability at location

**TMF629 (Customer Management):**
- `GET /tmf629/customer/{customerId}` - Get customer information
- `POST /tmf629/customer` - Create customer
- `PATCH /tmf629/customer/{customerId}` - Update customer
- `DELETE /tmf629/customer/{customerId}` - Delete customer

**TMF622 (Product Ordering):**
- `POST /tmf622/productOrder` - Create product order
- `GET /tmf622/productOrder` - List orders with filtering
- `GET /tmf622/productOrder/{orderId}` - Get order by ID
- `PATCH /tmf622/productOrder/{orderId}` - Update order
- `POST /tmf622/productOrder/{orderId}/cancel` - Cancel order
- `DELETE /tmf622/productOrder/{orderId}` - Delete order (permanent)

**TMF640 (Service Activation):**
- `POST /tmf640/serviceActivation` - Activate service in network

**Catalog Management (Internal):**
- `GET /api/service-specifications` - List service specs
- `GET /api/product-offerings` - List product offerings
- `GET /api/geographic-locations` - List coverage areas
- `POST /api/service-specification` - Create service spec
- `POST /api/product-offering` - Create product offering
- `POST /api/product-offering/{offerId}/link-service` - Link offering to service
- `GET /api/catalog-integrity` - Validate catalog integrity
- `GET /health` - Health check

## MCP Tool Invocation Flow

1. Claude Desktop client invokes MCP tool (e.g., `customer_management`)
2. HTTP streaming request sent to `http://localhost:8090/mcp` (Claude Desktop config)
3. MCP server (`mcp_fastmcp_server_extended.py`) receives request
4. MCP tool handler creates aiohttp session and calls catalog manager API
5. Catalog manager queries PostgreSQL database
6. Response returned through MCP server back to Claude Desktop
7. Audit entry logged (timestamp, correlationId, action, request, response, status)

---

*Integration audit: 2026-04-07*
