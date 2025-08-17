#!/usr/bin/env python3
"""
Enhanced MCP Server for Telepath AI - Uses FastMCP for HTTP streaming
Extended with new catalog management tools
"""

import os
import logging
import asyncio
import json
import aiohttp
from typing import Dict, Any, List, Optional, Union
from mcp.server.fastmcp import FastMCP

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
PORT = os.getenv("PORT", "8090")
HOST = os.getenv("HOST", "0.0.0.0")
CATALOG_MANAGER_URL = "http://catalog-manager:8080"
DEFAULT_TIMEOUT = 30

# Create the MCP server
mcp = FastMCP("telepath-mcp", port=PORT, host=HOST, debug=True, log_level="INFO")

# Global session for HTTP requests
session = None

async def ensure_session():
    """Ensure aiohttp session is created"""
    global session
    if session is None:
        session = aiohttp.ClientSession()

async def cleanup_session():
    """Cleanup aiohttp session"""
    global session
    if session:
        await session.close()
        session = None

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

# ============================================================================
# RESOURCES for browsing data
# ============================================================================

@mcp.resource("customers://list")
async def list_customers() -> str:
    """Get a list of all customers with their details"""
    await ensure_session()
    
    url = f"{CATALOG_MANAGER_URL}/api/customers"
    async with session.get(url, timeout=DEFAULT_TIMEOUT) as response:
        customers = await response.json()
        return json.dumps(customers, indent=2)

@mcp.resource("services://catalog")
async def get_service_catalog() -> str:
    """Get the complete service catalog with all available services"""
    await ensure_session()
    
    url = f"{CATALOG_MANAGER_URL}/api/service-specifications?include_offerings=true"
    async with session.get(url, timeout=DEFAULT_TIMEOUT) as response:
        services = await response.json()
        return json.dumps(services, indent=2)

@mcp.resource("products://catalog")
async def get_product_catalog() -> str:
    """Get the complete product catalog with all available offerings"""
    await ensure_session()
    
    url = f"{CATALOG_MANAGER_URL}/api/product-offerings?include_services=true"
    async with session.get(url, timeout=DEFAULT_TIMEOUT) as response:
        products = await response.json()
        return json.dumps(products, indent=2)

@mcp.resource("coverage://map")
async def get_coverage_map() -> str:
    """Get service coverage by location showing what services are available where"""
    await ensure_session()
    
    url = f"{CATALOG_MANAGER_URL}/api/geographic-locations?include_coverage=true"
    async with session.get(url, timeout=DEFAULT_TIMEOUT) as response:
        coverage = await response.json()
        return json.dumps(coverage, indent=2)

@mcp.resource("customer://{customer_id}")
async def get_customer_details(customer_id: str) -> str:
    """Get detailed information about a specific customer including their services"""
    await ensure_session()
    
    # Get customer info
    url = f"{CATALOG_MANAGER_URL}/tmf629/customer/{customer_id}"
    async with session.get(url, timeout=DEFAULT_TIMEOUT) as response:
        if response.status == 404:
            return json.dumps({"error": "Customer not found"}, indent=2)
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
    """Get recent orders from the system showing latest customer activity using TMF622 format"""
    await ensure_session()
    
    url = f"{CATALOG_MANAGER_URL}/tmf622/productOrder?limit=10"
    async with session.get(url, timeout=DEFAULT_TIMEOUT) as response:
        orders = await response.json()
        return json.dumps(orders, indent=2)

@mcp.resource("orders://customer/{customer_id}")
async def get_customer_orders(customer_id: str) -> str:
    """Get all orders for a specific customer using TMF622 format"""
    await ensure_session()
    
    url = f"{CATALOG_MANAGER_URL}/tmf622/productOrder?relatedParty.id={customer_id}"
    async with session.get(url, timeout=DEFAULT_TIMEOUT) as response:
        if response.status == 404:
            return json.dumps({"error": "No orders found for customer"}, indent=2)
        orders = await response.json()
        return json.dumps(orders, indent=2)

@mcp.resource("catalog://integrity")
async def get_catalog_integrity() -> str:
    """Get catalog integrity status and recent validation results"""
    await ensure_session()
    
    url = f"{CATALOG_MANAGER_URL}/api/catalog-integrity"
    async with session.get(url, timeout=DEFAULT_TIMEOUT) as response:
        integrity = await response.json()
        return json.dumps(integrity, indent=2)

# ============================================================================
# EXISTING TOOLS (TMF Forum APIs)
# ============================================================================

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
    await ensure_session()
    
    url = f"{CATALOG_MANAGER_URL}/tmf637/serviceQualification"
    request_data = {
        "address": address,
        "serviceSpecification": serviceSpecification
    }
    
    try:
        async with session.post(url, json=request_data, timeout=DEFAULT_TIMEOUT) as response:
            result = await response.json()
            log_audit("service_qualification", request_data, result)
            return result
    except Exception as e:
        error_result = {"error": str(e)}
        log_audit("service_qualification", request_data, error_result)
        raise Exception(f"Service qualification failed: {str(e)}")

@mcp.tool()
async def customer_management(customerId: str) -> Dict[str, Any]:
    """Get customer information including account status and eligibility (TMF629)
    
    Args:
        customerId: The customer ID to look up
    
    Returns:
        Customer information
    """
    await ensure_session()
    
    url = f"{CATALOG_MANAGER_URL}/tmf629/customer/{customerId}"
    
    try:
        async with session.get(url, timeout=DEFAULT_TIMEOUT) as response:
            result = await response.json()
            log_audit("customer_management", {"customerId": customerId}, result)
            return result
    except Exception as e:
        error_result = {"error": str(e)}
        log_audit("customer_management", {"customerId": customerId}, error_result)
        raise Exception(f"Customer lookup failed: {str(e)}")

@mcp.tool()
async def product_ordering(
    orderDate: str,
    externalId: str,
    customerId: str,
    productOfferingId: str,
    address: Dict[str, str]
) -> Dict[str, Any]:
    """Create a product order for a customer (TMF622)
    
    Args:
        orderDate: Order date
        externalId: External order ID
        customerId: Customer ID
        productOfferingId: Product offering ID
        address: Delivery address
    
    Returns:
        Created order information
    """
    await ensure_session()
    
    url = f"{CATALOG_MANAGER_URL}/tmf622/productOrder"
    
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
    
    try:
        async with session.post(url, json=order_data, timeout=DEFAULT_TIMEOUT) as response:
            result = await response.json()
            log_audit("product_ordering", order_data, result)
            return result
    except Exception as e:
        error_result = {"error": str(e)}
        log_audit("product_ordering", order_data, error_result)
        raise Exception(f"Product ordering failed: {str(e)}")

@mcp.tool()
async def service_activation(
    serviceName: str,
    serviceType: str,
    address: Dict[str, str],
    serviceSpecificationId: str
) -> Dict[str, Any]:
    """Activate a service in the network (TMF640)
    
    Args:
        serviceName: Service name
        serviceType: Service type (e.g., "Broadband")
        address: Service address
        serviceSpecificationId: Service specification ID
    
    Returns:
        Service activation result
    """
    await ensure_session()
    
    url = f"{CATALOG_MANAGER_URL}/tmf640/serviceActivation"
    
    # Transform to TMF640 format
    activation_data = {
        "service": {
            "name": serviceName,
            "serviceType": serviceType,
            "place": address,
            "serviceSpecification": {
                "id": serviceSpecificationId
            }
        }
    }
    
    try:
        async with session.post(url, json=activation_data, timeout=DEFAULT_TIMEOUT) as response:
            result = await response.json()
            log_audit("service_activation", activation_data, result)
            return result
    except Exception as e:
        error_result = {"error": str(e)}
        log_audit("service_activation", activation_data, error_result)
        raise Exception(f"Service activation failed: {str(e)}")

@mcp.tool()
async def order_management(
    orderId: Optional[str] = None,
    customerId: Optional[str] = None,
    limit: int = 10,
    offset: int = 0
) -> Union[List, Dict]:
    """List and retrieve product orders using TMF622 standard (supports filtering by customer)
    
    Args:
        orderId: Optional: Get specific order by ID
        customerId: Optional: Filter orders by customer ID
        limit: Maximum number of orders to retrieve (default: 10)
        offset: Number of orders to skip for pagination (default: 0)
    
    Returns:
        List of orders in TMF622 format or specific order details
    """
    await ensure_session()
    
    # If specific order ID is requested, get that order
    if orderId:
        url = f"{CATALOG_MANAGER_URL}/tmf622/productOrder/{orderId}"
        request_data = {"orderId": orderId}
        
        try:
            async with session.get(url, timeout=DEFAULT_TIMEOUT) as response:
                if response.status == 404:
                    result = {"error": "Order not found"}
                else:
                    result = await response.json()
                log_audit("order_management_get_by_id", request_data, result)
                return result
        except Exception as e:
            error_result = {"error": str(e)}
            log_audit("order_management_get_by_id", request_data, error_result)
            raise Exception(f"Failed to retrieve order: {str(e)}")
    
    # Otherwise, list orders with optional filtering
    url = f"{CATALOG_MANAGER_URL}/tmf622/productOrder"
    params = {
        "limit": limit,
        "offset": offset
    }
    
    if customerId:
        params["relatedParty.id"] = customerId  # TMF622 standard parameter
    
    request_data = {"params": params}
    
    try:
        async with session.get(url, params=params, timeout=DEFAULT_TIMEOUT) as response:
            result = await response.json()
            log_audit("order_management_list", request_data, result)
            return result
    except Exception as e:
        error_result = {"error": str(e)}
        log_audit("order_management_list", request_data, error_result)
        raise Exception(f"Failed to retrieve orders: {str(e)}")

# ============================================================================
# NEW CATALOG MANAGEMENT TOOLS
# ============================================================================

@mcp.tool()
async def list_service_specifications(
    service_type: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
) -> Dict[str, Any]:
    """List/filter all service specifications
    
    Args:
        service_type: Filter by service type (e.g., 'fiber_internet', 'tv', 'mobile')
        search: Search in name and description
        limit: Maximum number of results (default 100)
        offset: Number of results to skip (default 0)
    
    Returns:
        List of service specifications with linked offerings count
    """
    await ensure_session()
    
    url = f"{CATALOG_MANAGER_URL}/api/service-specifications"
    params = {"limit": limit, "offset": offset}
    if service_type:
        params["service_type"] = service_type
    if search:
        params["search"] = search
    
    request_data = {"params": params}
    
    try:
        async with session.get(url, params=params, timeout=DEFAULT_TIMEOUT) as response:
            result = await response.json()
            log_audit("list_service_specifications", request_data, result)
            return result
    except Exception as e:
        error_result = {"error": str(e)}
        log_audit("list_service_specifications", request_data, error_result)
        raise Exception(f"Failed to list service specifications: {str(e)}")

@mcp.tool()
async def list_product_offerings(
    category: Optional[str] = None,
    is_active: Optional[bool] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    search: Optional[str] = None,
    include_services: bool = True,
    limit: int = 100,
    offset: int = 0
) -> Dict[str, Any]:
    """List/filter all product offerings
    
    Args:
        category: Filter by category (e.g., 'internet', 'tv', 'mobile', 'bundle')
        is_active: Filter by active status
        min_price: Minimum monthly price filter
        max_price: Maximum monthly price filter
        search: Search in name and description
        include_services: Include linked service specifications in results
        limit: Maximum number of results (default 100)
        offset: Number of results to skip (default 0)
    
    Returns:
        List of product offerings with optional linked services
    """
    await ensure_session()
    
    url = f"{CATALOG_MANAGER_URL}/api/product-offerings"
    params = {"limit": limit, "offset": offset, "include_services": str(include_services).lower()}
    if category:
        params["category"] = category
    if is_active is not None:
        params["is_active"] = str(is_active).lower()
    if min_price is not None:
        params["min_price"] = min_price
    if max_price is not None:
        params["max_price"] = max_price
    if search:
        params["search"] = search
    
    request_data = {"params": params}
    
    try:
        async with session.get(url, params=params, timeout=DEFAULT_TIMEOUT) as response:
            result = await response.json()
            log_audit("list_product_offerings", request_data, result)
            return result
    except Exception as e:
        error_result = {"error": str(e)}
        log_audit("list_product_offerings", request_data, error_result)
        raise Exception(f"Failed to list product offerings: {str(e)}")

@mcp.tool()
async def list_geographic_locations(
    city: Optional[str] = None,
    state_province: Optional[str] = None,
    has_coverage: Optional[bool] = None,
    service_type: Optional[str] = None,
    include_coverage: bool = True,
    limit: int = 100,
    offset: int = 0
) -> Dict[str, Any]:
    """List locations with coverage info
    
    Args:
        city: Filter by city
        state_province: Filter by state/province
        has_coverage: Filter locations with/without coverage
        service_type: Filter by specific service type coverage
        include_coverage: Include detailed coverage information
        limit: Maximum number of results (default 100)
        offset: Number of results to skip (default 0)
    
    Returns:
        List of geographic locations with coverage details
    """
    await ensure_session()
    
    url = f"{CATALOG_MANAGER_URL}/api/geographic-locations"
    params = {"limit": limit, "offset": offset, "include_coverage": str(include_coverage).lower()}
    if city:
        params["city"] = city
    if state_province:
        params["state_province"] = state_province
    if has_coverage is not None:
        params["has_coverage"] = str(has_coverage).lower()
    if service_type:
        params["service_type"] = service_type
    
    request_data = {"params": params}
    
    try:
        async with session.get(url, params=params, timeout=DEFAULT_TIMEOUT) as response:
            result = await response.json()
            log_audit("list_geographic_locations", request_data, result)
            return result
    except Exception as e:
        error_result = {"error": str(e)}
        log_audit("list_geographic_locations", request_data, error_result)
        raise Exception(f"Failed to list geographic locations: {str(e)}")

@mcp.tool()
async def sync_catalog_data(
    sync_type: str = "full"
) -> Dict[str, Any]:
    """Validate and sync catalog integrity
    
    Args:
        sync_type: Type of sync to perform ('full', 'integrity_check', 'coverage_sync')
    
    Returns:
        Sync operation results with validation status
    """
    await ensure_session()
    
    url = f"{CATALOG_MANAGER_URL}/api/sync-catalog-data"
    request_data = {"sync_type": sync_type}
    
    try:
        async with session.post(url, json=request_data, timeout=DEFAULT_TIMEOUT) as response:
            result = await response.json()
            log_audit("sync_catalog_data", request_data, result)
            return result
    except Exception as e:
        error_result = {"error": str(e)}
        log_audit("sync_catalog_data", request_data, error_result)
        raise Exception(f"Catalog sync failed: {str(e)}")

@mcp.tool()
async def create_service_specification(
    name: str,
    service_type: str,
    description: str,
    id: Optional[str] = None
) -> Dict[str, Any]:
    """Create new service specification
    
    Args:
        name: Service specification name
        service_type: Type of service (e.g., 'fiber_internet', 'tv', 'mobile')
        description: Detailed description of the service
        id: Optional custom ID (auto-generated if not provided)
    
    Returns:
        Created service specification details
    """
    await ensure_session()
    
    url = f"{CATALOG_MANAGER_URL}/api/service-specifications"
    request_data = {
        "name": name,
        "service_type": service_type,
        "description": description
    }
    if id:
        request_data["id"] = id
    
    try:
        async with session.post(url, json=request_data, timeout=DEFAULT_TIMEOUT) as response:
            result = await response.json()
            log_audit("create_service_specification", request_data, result)
            return result
    except Exception as e:
        error_result = {"error": str(e)}
        log_audit("create_service_specification", request_data, error_result)
        raise Exception(f"Failed to create service specification: {str(e)}")

@mcp.tool()
async def create_product_offering(
    name: str,
    description: str,
    category: str,
    price_monthly: float,
    price_setup: float = 0.0,
    contract_length_months: int = 0,
    is_active: bool = True,
    id: Optional[str] = None
) -> Dict[str, Any]:
    """Create new product offering
    
    Args:
        name: Product offering name
        description: Detailed description
        category: Product category (e.g., 'internet', 'tv', 'mobile', 'bundle')
        price_monthly: Monthly price in dollars
        price_setup: One-time setup fee (default 0.0)
        contract_length_months: Contract length in months (default 0 for no contract)
        is_active: Whether the offering is active (default True)
        id: Optional custom ID (auto-generated if not provided)
    
    Returns:
        Created product offering details
    """
    await ensure_session()
    
    url = f"{CATALOG_MANAGER_URL}/api/product-offerings"
    request_data = {
        "name": name,
        "description": description,
        "category": category,
        "price_monthly": price_monthly,
        "price_setup": price_setup,
        "contract_length_months": contract_length_months,
        "is_active": is_active
    }
    if id:
        request_data["id"] = id
    
    try:
        async with session.post(url, json=request_data, timeout=DEFAULT_TIMEOUT) as response:
            result = await response.json()
            log_audit("create_product_offering", request_data, result)
            return result
    except Exception as e:
        error_result = {"error": str(e)}
        log_audit("create_product_offering", request_data, error_result)
        raise Exception(f"Failed to create product offering: {str(e)}")

@mcp.tool()
async def link_offering_to_specification(
    product_offering_id: str,
    service_specification_id: str,
    is_primary: bool = False
) -> Dict[str, Any]:
    """Link product offering to service specification
    
    Args:
        product_offering_id: ID of the product offering
        service_specification_id: ID of the service specification to link
        is_primary: Whether this is the primary service for the offering
    
    Returns:
        Link creation result
    """
    await ensure_session()
    
    url = f"{CATALOG_MANAGER_URL}/api/link-offering-to-specification"
    request_data = {
        "product_offering_id": product_offering_id,
        "service_specification_id": service_specification_id,
        "is_primary": is_primary
    }
    
    try:
        async with session.post(url, json=request_data, timeout=DEFAULT_TIMEOUT) as response:
            result = await response.json()
            log_audit("link_offering_to_specification", request_data, result)
            return result
    except Exception as e:
        error_result = {"error": str(e)}
        log_audit("link_offering_to_specification", request_data, error_result)
        raise Exception(f"Failed to link offering to specification: {str(e)}")

@mcp.tool()
async def add_geographic_coverage(
    location_id: str,
    service_type: str,
    available: bool = True,
    max_speed_mbps: Optional[int] = None,
    coverage_quality: str = "good",
    technology: Optional[str] = None,
    signal_strength: Optional[int] = None
) -> Dict[str, Any]:
    """Add coverage area for services
    
    Args:
        location_id: Geographic location ID
        service_type: Type of service coverage to add
        available: Whether service is available (default True)
        max_speed_mbps: Maximum speed in Mbps for internet services
        coverage_quality: Coverage quality ('excellent', 'good', 'fair', 'poor')
        technology: Technology used ('fiber', 'cable', 'dsl', 'wireless', '5G', etc.)
        signal_strength: Signal strength (1-5 scale for wireless services)
    
    Returns:
        Coverage addition result
    """
    await ensure_session()
    
    url = f"{CATALOG_MANAGER_URL}/api/add-geographic-coverage"
    request_data = {
        "location_id": location_id,
        "service_type": service_type,
        "available": available,
        "coverage_quality": coverage_quality
    }
    if max_speed_mbps is not None:
        request_data["max_speed_mbps"] = max_speed_mbps
    if technology:
        request_data["technology"] = technology
    if signal_strength is not None:
        request_data["signal_strength"] = signal_strength
    
    try:
        async with session.post(url, json=request_data, timeout=DEFAULT_TIMEOUT) as response:
            result = await response.json()
            log_audit("add_geographic_coverage", request_data, result)
            return result
    except Exception as e:
        error_result = {"error": str(e)}
        log_audit("add_geographic_coverage", request_data, error_result)
        raise Exception(f"Failed to add geographic coverage: {str(e)}")

if __name__ == "__main__":
    print(f"Running Enhanced Telepath MCP Server on {HOST}:{PORT}")
    print(f"Catalog Manager URL: {CATALOG_MANAGER_URL}")
    print(f"Available tools: 13 (5 TMF Forum + 8 Catalog Management)")
    try:
        mcp.run(transport="streamable-http")
    finally:
        # Cleanup session if exists
        if session:
            asyncio.run(cleanup_session())
