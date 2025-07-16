#!/usr/bin/env python3
"""
MCP Server for Telepath AI - Fixed version using FastMCP for HTTP streaming
"""

import os
import logging
import asyncio
import json
import aiohttp
from typing import Dict, Any
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

def log_audit(action: str, request: Dict, response: Dict):
    """Log audit trail for compliance"""
    from datetime import datetime
    audit_entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "correlationId": f"{action}-{datetime.utcnow().timestamp()}",
        "action": action,
        "requestPayload": request,
        "responsePayload": response,
        "status": "Success" if "error" not in response else "Failed"
    }
    logger.info(f"Audit: {audit_entry}")

# Resources for browsing data
@mcp.resource("customers://list")
async def list_customers() -> str:
    """Get a list of all customers with their details"""
    await ensure_session()
    
    url = f"{CATALOG_MANAGER_URL}/api/customers"
    try:
        async with session.get(url, timeout=DEFAULT_TIMEOUT) as response:
            customers = await response.json()
            return json.dumps(customers, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Failed to fetch customers: {str(e)}"}, indent=2)

@mcp.resource("services://catalog")
async def get_service_catalog() -> str:
    """Get the complete service catalog with all available services"""
    await ensure_session()
    
    url = f"{CATALOG_MANAGER_URL}/api/service-specifications"
    try:
        async with session.get(url, timeout=DEFAULT_TIMEOUT) as response:
            services = await response.json()
            # Group by service type for better readability
            grouped = {}
            for service in services:
                service_type = service.get('service_type', 'Unknown')
                if service_type not in grouped:
                    grouped[service_type] = []
                grouped[service_type].append(service)
            return json.dumps(grouped, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Failed to fetch service catalog: {str(e)}"}, indent=2)

@mcp.resource("coverage://map")
async def get_coverage_map() -> str:
    """Get service coverage by location showing what services are available where"""
    await ensure_session()
    
    url = f"{CATALOG_MANAGER_URL}/api/service-coverage"
    try:
        async with session.get(url, timeout=DEFAULT_TIMEOUT) as response:
            coverage = await response.json()
            return json.dumps(coverage, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Failed to fetch coverage map: {str(e)}"}, indent=2)

@mcp.resource("customer://{customer_id}")
async def get_customer_details(customer_id: str) -> str:
    """Get detailed information about a specific customer including their services"""
    await ensure_session()
    
    try:
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
    except Exception as e:
        return json.dumps({"error": f"Failed to fetch customer details: {str(e)}"}, indent=2)

@mcp.resource("orders://recent")
async def get_recent_orders() -> str:
    """Get recent orders from the system showing latest customer activity"""
    await ensure_session()
    
    url = f"{CATALOG_MANAGER_URL}/api/orders/recent"
    try:
        async with session.get(url, timeout=DEFAULT_TIMEOUT) as response:
            orders = await response.json()
            return json.dumps(orders, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Failed to fetch recent orders: {str(e)}"}, indent=2)

# Tools for performing actions

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

# Additional catalog management tools

@mcp.tool()
async def list_service_specifications(category: str = None) -> Dict[str, Any]:
    """List all available service specifications (TMF633)
    
    Args:
        category: Optional category filter
    
    Returns:
        List of service specifications
    """
    await ensure_session()
    
    url = f"{CATALOG_MANAGER_URL}/tmf633/serviceSpecification"
    params = {}
    if category:
        params["category"] = category
    
    try:
        async with session.get(url, params=params, timeout=DEFAULT_TIMEOUT) as response:
            result = await response.json()
            log_audit("list_service_specifications", {"category": category}, result)
            return result
    except Exception as e:
        error_result = {"error": str(e)}
        log_audit("list_service_specifications", {"category": category}, error_result)
        raise Exception(f"Failed to list service specifications: {str(e)}")

@mcp.tool()
async def list_product_offerings(category: str = None, isBundle: bool = None) -> Dict[str, Any]:
    """List all available product offerings (TMF620)
    
    Args:
        category: Optional category filter
        isBundle: Filter for bundle vs individual offerings
    
    Returns:
        List of product offerings
    """
    await ensure_session()
    
    url = f"{CATALOG_MANAGER_URL}/tmf620/productOffering"
    params = {}
    if category:
        params["category"] = category
    if isBundle is not None:
        params["isBundle"] = isBundle
    
    try:
        async with session.get(url, params=params, timeout=DEFAULT_TIMEOUT) as response:
            result = await response.json()
            log_audit("list_product_offerings", {"category": category, "isBundle": isBundle}, result)
            return result
    except Exception as e:
        error_result = {"error": str(e)}
        log_audit("list_product_offerings", {"category": category, "isBundle": isBundle}, error_result)
        raise Exception(f"Failed to list product offerings: {str(e)}")

if __name__ == "__main__":
    print(f"Running Telepath MCP Server on {HOST}:{PORT}")
    print(f"Catalog Manager URL: {CATALOG_MANAGER_URL}")
    try:
        mcp.run(transport="streamable-http")
    finally:
        # Cleanup session if exists
        if session:
            asyncio.run(cleanup_session())