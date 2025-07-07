#!/usr/bin/env python3
"""
Example of adding Resources to the Telepath MCP Server
"""

# Add this to the FastMCP server

@mcp.resource("customers://list")
async def list_customers() -> str:
    """Get a list of all customers"""
    await ensure_session()
    
    url = f"{CATALOG_MANAGER_URL}/api/customers"
    async with session.get(url, timeout=DEFAULT_TIMEOUT) as response:
        customers = await response.json()
        return json.dumps(customers, indent=2)

@mcp.resource("services://catalog")
async def get_service_catalog() -> str:
    """Get the complete service catalog"""
    await ensure_session()
    
    url = f"{CATALOG_MANAGER_URL}/api/service-specifications"
    async with session.get(url, timeout=DEFAULT_TIMEOUT) as response:
        services = await response.json()
        return json.dumps(services, indent=2)

@mcp.resource("coverage://map")
async def get_coverage_map() -> str:
    """Get service coverage by location"""
    await ensure_session()
    
    url = f"{CATALOG_MANAGER_URL}/api/service-coverage"
    async with session.get(url, timeout=DEFAULT_TIMEOUT) as response:
        coverage = await response.json()
        return json.dumps(coverage, indent=2)

@mcp.resource("customer://{customer_id}")
async def get_customer_details(customer_id: str) -> str:
    """Get detailed information about a specific customer"""
    await ensure_session()
    
    url = f"{CATALOG_MANAGER_URL}/tmf629/customer/{customer_id}"
    async with session.get(url, timeout=DEFAULT_TIMEOUT) as response:
        customer = await response.json()
        
    # Get active services for this customer
    services_url = f"{CATALOG_MANAGER_URL}/api/customer/{customer_id}/services"
    async with session.get(services_url, timeout=DEFAULT_TIMEOUT) as response:
        services = await response.json()
        
    return json.dumps({
        "customer": customer,
        "active_services": services
    }, indent=2)

@mcp.resource("orders://recent")
async def get_recent_orders() -> str:
    """Get recent orders from the system"""
    await ensure_session()
    
    url = f"{CATALOG_MANAGER_URL}/api/orders/recent"
    async with session.get(url, timeout=DEFAULT_TIMEOUT) as response:
        orders = await response.json()
        return json.dumps(orders, indent=2)
