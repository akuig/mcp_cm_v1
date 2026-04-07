# Coding Conventions

**Analysis Date:** 2026-04-07

## Naming Patterns

**Files:**
- Lowercase with underscores: `catalog_manager_enhanced.py`, `mcp_fastmcp_server_extended.py`
- Test files use `test_` prefix: `test_enhanced.py`, `test_order_lifecycle.py`
- Backup/archive files append version timestamps: `catalog_manager_extended.py.backup.20250812_101748`

**Functions:**
- snake_case throughout: `ensure_session()`, `cleanup_session()`, `log_audit()`, `list_service_specifications()`
- Async functions use `async def`: `async def service_qualification()`, `async def customer_management()`
- Private/internal functions start with underscore (not observed in codebase - all functions are public)

**Variables:**
- snake_case for local variables: `order_data`, `request_data`, `error_result`, `params`
- SCREAMING_SNAKE_CASE for constants: `CATALOG_MANAGER_URL`, `DEFAULT_TIMEOUT`, `PORT`, `HOST`
- Global session variable: `session` (with explicit `global session` declarations)

**Types:**
- Type hints used extensively throughout: `Dict[str, Any]`, `List`, `Optional[str]`, `Union[List, Dict]`
- Return type hints on all functions: `-> Dict[str, Any]`, `-> Union[List, Dict]`, `-> str`

**Classes:**
- PascalCase for class names: `EnhancedMCPTester`, `Colors`
- Test classes use `Tester` suffix and context manager pattern: `__init__()`, `__aenter__()`, `__aexit__()`

## Code Style

**Formatting:**
- No explicit formatter configuration (no `.prettier` or `black` config found)
- Line length appears to be around 100-120 characters based on code samples
- Indentation: 4 spaces (standard Python)
- Imports: Standard library, then third-party, then local (PEP 8 style)

**Linting:**
- No `.eslintrc` or `pylintrc` found
- Uses pytest (in requirements.txt: `pytest==7.4.3`, `pytest-asyncio==0.21.1`)
- Type hints suggest adherence to Python typing conventions

## Import Organization

**Order:**
1. Standard library imports (`os`, `logging`, `asyncio`, `json`)
2. Third-party async/web imports (`aiohttp`)
3. Typing imports (`from typing import Dict, Any, List, Optional, Union`)
4. Framework imports (`from mcp.server.fastmcp import FastMCP`)

Example from `mcp_fastmcp_server_extended.py` (lines 7-13):
```python
import os
import logging
import asyncio
import json
import aiohttp
from typing import Dict, Any, List, Optional, Union
from mcp.server.fastmcp import FastMCP
```

**Path Aliases:**
- No path aliases or custom import paths observed in MCP codebase
- All imports use absolute paths

## Error Handling

**Pattern:**
- Wrap all HTTP/async operations in try-except blocks
- Catch broad `Exception` for network failures, parse errors, timeouts
- Always log errors with audit trail
- Create error dict with "error" key: `{"error": str(e)}`
- Re-raise with context message: `raise Exception(f"Service qualification failed: {str(e)}")`

Example from `mcp_fastmcp_server_extended.py` (lines 181-189):
```python
try:
    async with session.post(url, json=request_data, timeout=DEFAULT_TIMEOUT) as response:
        result = await response.json()
        log_audit("service_qualification", request_data, result)
        return result
except Exception as e:
    error_result = {"error": str(e)}
    log_audit("service_qualification", request_data, error_result)
    raise Exception(f"Service qualification failed: {str(e)}")
```

**HTTP Status Handling:**
- Check `response.status` for specific status codes (404, 400)
- Return error dict for 404: `{"error": "Order not found"}`
- Always parse JSON response on non-error paths

## Logging

**Framework:** Python `logging` module with structured JSON logging

**Configuration** from `mcp_fastmcp_server_extended.py` (lines 16-17):
```python
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
```

**Audit Logging Pattern:**
- Every MCP tool call logged with `log_audit()` function
- Captures: timestamp, correlationId, action, requestPayload, responsePayload, status
- Status determined by checking for errors in response

Example from `mcp_fastmcp_server_extended.py` (lines 44-55):
```python
def log_audit(action: str, request: Dict, response: Union[Dict, List]):
    """Log audit trail for compliance"""
    from datetime import datetime
    audit_entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "correlationId": f"{action}-{datetime.utcnow().timestamp()}",
        "action": action,
        "requestPayload": request,
        "responsePayload": response,
        "status": "Success" if (isinstance(response, list) or "error" not in response) else "Failed"
    }
    logger.info(f"Audit: {audit_entry}")
```

**Test Logging:**
- ANSI color codes for terminal output (Colors class with RED, GREEN, YELLOW, BLUE, etc.)
- Helper functions: `print_test()`, `print_success()`, `print_error()`, `print_warning()`, `print_info()`
- No structured JSON logging in tests, purely formatted stdout

## Comments

**When to Comment:**
- Function/method docstrings required on all public functions
- Docstrings explain parameters, return values, and purpose
- Section separators (divider comments) used to organize large files

Example from `mcp_fastmcp_server_extended.py` (lines 159-172):
```python
@mcp.tool()
async def service_qualification(
    address: Dict[str, str],
    serviceSpecification: Dict[str, str]
) -> Dict[str, Any]:
    """Check if a service is available at a specific location (TMF637)

    Args:
        address: Address with streetName, streetNumber, and city
        serviceSpecification: Service specification with id and name

    Returns:
        Service qualification result
    """
```

**Docstring Style:**
- Triple-quote docstrings with description, Args, and Returns sections
- Args section lists parameter names and descriptions
- Returns section describes return value type and content

## Function Design

**Size:** Functions are typically 10-40 lines for MCP tools

**Parameters:**
- Function parameters match MCP tool input requirements
- Default values for optional parameters (limit=10, offset=0, is_active=None)
- Type hints on all parameters

**Return Values:**
- Consistently return Dict[str, Any] for tool responses
- May return Union[List, Dict] for list/single endpoints
- Always return JSON-serializable structures (dicts, lists, primitives)

**Async Pattern:**
- All HTTP-calling functions are `async def`
- Use `async with session.{get,post,patch,delete}()` pattern
- Call `await ensure_session()` at start of every tool function
- Await JSON parsing: `result = await response.json()`

## Module Design

**Exports:**
- No explicit `__all__` definitions found
- MCP tools exported via `@mcp.tool()` decorator
- Resources exported via `@mcp.resource()` decorator
- Helper functions (log_audit, ensure_session, cleanup_session) at module level

**FastMCP Server Structure** from `mcp_fastmcp_server_extended.py`:
1. Configuration (PORT, HOST, CATALOG_MANAGER_URL, DEFAULT_TIMEOUT)
2. MCP server initialization: `mcp = FastMCP("telepath-mcp", port=PORT, host=HOST, debug=True, log_level="INFO")`
3. Session management functions (ensure_session, cleanup_session)
4. Audit logging function
5. Resource definitions (@mcp.resource)
6. Tool definitions (@mcp.tool)
7. Main entry point with `mcp.run(transport="streamable-http")`

**Barrel Files:**
- Not used in this codebase - no index.py files

## TMF Forum Compliance

**API Response Handling:**
- Payload format must handle both list and dict responses (known issue/pitfall)
- When endpoint returns list: return as-is
- When endpoint returns dict: wrap or return with metadata
- Tools must transform to/from TMF format (e.g., TMF622, TMF629, TMF637, TMF640)

Example transformation from `mcp_fastmcp_server_extended.py` (lines 240-256):
```python
# Transform to TMF622 format
order_data = {
    "orderDate": orderDate,
    "externalId": externalId,
    "relatedParty": [{
        "id": customerId,
        "role": "customer"
    }],
    "orderItem": [{
        "action": "add",
        "productOffering": {
            "id": productOfferingId
        },
        "product": {
            "place": address
        }
    }]
}
```

## MCP Tool Decoration

**Pattern:**
- Use `@mcp.tool()` decorator (no arguments)
- Place docstring immediately after function signature
- Tools are async methods on FastMCP instance

**Resources Pattern:**
- Use `@mcp.resource()` decorator with URI template
- Example: `@mcp.resource("customers://list")`
- Return string content (typically JSON.dumps)

---

*Convention analysis: 2026-04-07*
