# Technology Stack

**Analysis Date:** 2026-04-07

## Languages

**Primary:**
- Python 3.11 - FastAPI/Flask REST APIs, MCP server implementation, database connectivity

**Secondary:**
- SQL - PostgreSQL schema definition and data manipulation

## Runtime

**Environment:**
- Python 3.11-slim (Docker base image)
- Linux containers (Alpine-based PostgreSQL)

**Package Manager:**
- pip - Python package management
- Lockfile: Not detected (requirements.txt files used instead)

## Frameworks

**Core:**
- Flask 2.3.3+ - REST API framework for catalog manager (`src/catalog_manager_enhanced.py` runs as `catalog_manager.py` in container)
- Werkzeug 2.3.7+ - WSGI utilities for Flask

**MCP & Async:**
- mcp (>= 0.1.0) - Model Context Protocol SDK for MCP server
- FastMCP - HTTP streaming wrapper for MCP server (`mcp_fastmcp_server_extended.py`)
- aiohttp 3.8.5-3.9.1 - Async HTTP client for inter-service communication

**Build/Dev:**
- Gunicorn 21.2.0 - Production WSGI server (optional, configured in requirements)
- Docker Compose - Container orchestration for local development and deployment
- pytest 7.4.3 - Testing framework
- pytest-asyncio 0.21.1 - Async test support

## Key Dependencies

**Critical:**
- psycopg2-binary 2.9.7+ - PostgreSQL adapter for Python (enables database connectivity)
- requests 2.31.0 - HTTP client library for synchronous requests

**Infrastructure:**
- python-dotenv 1.0.0 - Environment variable management from `.env` files
- python-json-logger 2.0.7 - Structured JSON logging for audit trails
- jsonschema 4.20.0 - JSON schema validation for API payloads
- Flask-CORS 4.0.0 - CORS support for API endpoints
- pyyaml 6.0+ - YAML parsing for demo reset configuration

## Configuration

**Environment:**
- Environment variables via `python-dotenv` - `.env` file (not committed)
- Required variables:
  - `DB_HOST` - PostgreSQL host (default: `postgres`)
  - `DB_PORT` - PostgreSQL port (default: `5432`)
  - `DB_NAME` - Database name (default: `telecom_catalog`)
  - `DB_USER` - Database user (default: `telecom_user`)
  - `DB_PASSWORD` - Database password (default: `telecom_pass`)
  - `CATALOG_MANAGER_URL` - Base URL for catalog manager API (default: `http://catalog-manager:8080`)
  - `PORT` - MCP server port (default: `8090`)
  - `HOST` - MCP server bind address (default: `0.0.0.0`)

**Build:**
- `docker-compose.yml` - Main orchestration for development (defines postgres, catalog-manager, mcp-server services)
- `Dockerfile.catalog.enhanced` - Build configuration for Flask catalog manager
- `Dockerfile.mcp.enhanced` - Build configuration for MCP server
- `init_db_extended.sql` - PostgreSQL schema and demo data initialization
- `config.yaml` - Demo reset tool configuration (demo customers, reset options, safety settings)

## Platform Requirements

**Development:**
- Python 3.11+
- Docker and Docker Compose
- PostgreSQL 15 (runs in container)
- System packages: curl, libpq-dev, gcc (installed in Dockerfile)

**Production:**
- Docker runtime
- PostgreSQL 15+ database instance
- Network connectivity between catalog-manager and mcp-server containers
- Port 8080 exposed for catalog manager API
- Port 8090 exposed for MCP server HTTP streaming

## API Port Mapping

| Service | Port | Purpose |
|---------|------|---------|
| Catalog Manager (Flask) | 8080 | REST API for TMF APIs (TMF622, TMF629, TMF637, TMF640) |
| MCP Server (HTTP Streaming) | 8090 | HTTP streaming endpoint for MCP tool invocation |
| PostgreSQL | 5432 | Database persistence |

## Deployment Notes

- MCP server uses HTTP streaming transport (`transport="streamable-http"` in FastMCP), not stdio
- Catalog manager and MCP server communicate via inter-container HTTP (service name resolution via Docker network `telecom_network`)
- Health checks configured on both Flask (GET `/health`) and PostgreSQL (pg_isready)
- Non-root user execution in containers (cataloguser/mcpuser, UID 1000)
- Structured JSON logging via python-json-logger for audit compliance

---

*Stack analysis: 2026-04-07*
