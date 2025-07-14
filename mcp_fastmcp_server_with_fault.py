#!/usr/bin/env python3
"""
MCP Server for Telepath AI - Uses FastMCP for HTTP streaming
Includes Fault Management capabilities
"""

import os
import logging
import asyncio
import json
import aiohttp
from typing import Dict, Any
from datetime import datetime
from mcp.server.fastmcp import FastMCP

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
PORT = os.getenv("PORT", "8090")
HOST = os.getenv("HOST", "0.0.0.0")
CATALOG_MANAGER_URL = "http://catalog-manager:8080"
FAULT_MANAGER_URL = "http://fault-manager:8081"
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
    audit_entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "correlationId": f"{action}-{datetime.utcnow().timestamp()}",
        "action": action,
        "requestPayload": request,
        "responsePayload": response,
        "status": "Success" if "error" not in response else "Failed"
    }
    logger.info(f"Audit: {json.dumps(audit_entry)}")

# Original TMF tools

@mcp.tool()
async def service_qualification(
    address: Dict[str, str],
    serviceSpecification: Dict[str, str]
) -> str:
    """Check if a service is available at a specific location (TMF637)
    
    Args:
        address: Address with streetName, streetNumber, and city
        serviceSpecification: Service specification with id and name
    
    Returns:
        Service qualification result
    """
    await ensure_session()
    
    url = f"{CATALOG_MANAGER_URL}/tmf637/serviceQualification"
    data = {
        "address": address,
        "serviceSpecification": serviceSpecification
    }
    
    try:
        async with session.post(url, json=data, timeout=DEFAULT_TIMEOUT) as response:
            result = await response.json()
            log_audit("service_qualification", data, result)
            return json.dumps(result, indent=2)
    except Exception as e:
        error_result = {"error": str(e)}
        log_audit("service_qualification", data, error_result)
        return json.dumps(error_result)

@mcp.tool()
async def customer_management(customerId: str) -> str:
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
            return json.dumps(result, indent=2)
    except Exception as e:
        error_result = {"error": str(e)}
        log_audit("customer_management", {"customerId": customerId}, error_result)
        return json.dumps(error_result)

@mcp.tool()
async def product_ordering(
    orderDate: str,
    externalId: str,
    customerId: str,
    productOfferingId: str,
    address: Dict[str, str]
) -> str:
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
    
    # Transform arguments to TMF622 format
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
            return json.dumps(result, indent=2)
    except Exception as e:
        error_result = {"error": str(e)}
        log_audit("product_ordering", order_data, error_result)
        return json.dumps(error_result)

@mcp.tool()
async def service_activation(
    serviceName: str,
    serviceType: str,
    address: Dict[str, str],
    serviceSpecificationId: str
) -> str:
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
    
    # Transform arguments to TMF640 format
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
            return json.dumps(result, indent=2)
    except Exception as e:
        error_result = {"error": str(e)}
        log_audit("service_activation", activation_data, error_result)
        return json.dumps(error_result)

# New Fault Management tools

@mcp.tool()
async def check_service_status(
    location: Dict[str, str] = None,
    serviceId: str = None
) -> str:
    """Check service status for a location or service, detect network faults and get recommended actions
    
    Args:
        location: Optional location with streetName, streetNumber, and city
        serviceId: Optional service ID to check specific service
    
    Returns:
        Service status with any problems, faults, and recommended actions
    """
    await ensure_session()
    
    url = f"{FAULT_MANAGER_URL}/serviceStatus/check"
    data = {}
    if location:
        data["location"] = location
    if serviceId:
        data["serviceId"] = serviceId
    
    try:
        async with session.post(url, json=data, timeout=DEFAULT_TIMEOUT) as response:
            result = await response.json()
            log_audit("check_service_status", data, result)
            return json.dumps(result, indent=2)
    except Exception as e:
        error_result = {"error": str(e)}
        log_audit("check_service_status", data, error_result)
        return json.dumps(error_result)

@mcp.tool()
async def create_trouble_ticket(
    description: str,
    customerId: str,
    severity: str = "minor",
    serviceId: str = None,
    contactPhone: str = None
) -> str:
    """Create a trouble ticket for customer reported issues (TMF621)
    
    Args:
        description: Description of the issue
        customerId: Customer ID
        severity: Severity level (critical, major, minor, warning, information)
        serviceId: Optional service ID affected
        contactPhone: Optional contact phone number
    
    Returns:
        Created trouble ticket information
    """
    await ensure_session()
    
    url = f"{FAULT_MANAGER_URL}/tmf621/troubleTicket"
    
    # Transform arguments to TMF621 format
    ticket_data = {
        "description": description,
        "severity": severity,
        "priority": 1 if severity in ["critical", "major"] else 3,
        "relatedParty": [{
            "id": customerId,
            "role": "customer",
            "name": f"Customer {customerId}"
        }],
        "serviceId": serviceId,
        "note": [{
            "text": f"Contact phone: {contactPhone}",
            "date": datetime.utcnow().isoformat()
        }] if contactPhone else []
    }
    
    try:
        async with session.post(url, json=ticket_data, timeout=DEFAULT_TIMEOUT) as response:
            result = await response.json()
            log_audit("create_trouble_ticket", ticket_data, result)
            return json.dumps(result, indent=2)
    except Exception as e:
        error_result = {"error": str(e)}
        log_audit("create_trouble_ticket", ticket_data, error_result)
        return json.dumps(error_result)

@mcp.tool()
async def execute_remedial_action(
    action: str,
    faultId: str = None
) -> str:
    """Execute recommended remedial actions for network issues
    
    Args:
        action: Action to execute (REROUTE_TRAFFIC, DISPATCH_TECHNICIAN, NOTIFY_CUSTOMERS)
        faultId: Optional ID of the network fault to address
    
    Returns:
        Action execution result
    """
    await ensure_session()
    
    url = f"{FAULT_MANAGER_URL}/serviceStatus/executeAction"
    data = {
        "action": action
    }
    if faultId:
        data["faultId"] = faultId
    
    try:
        async with session.post(url, json=data, timeout=DEFAULT_TIMEOUT) as response:
            result = await response.json()
            log_audit("execute_remedial_action", data, result)
            return json.dumps(result, indent=2)
    except Exception as e:
        error_result = {"error": str(e)}
        log_audit("execute_remedial_action", data, error_result)
        return json.dumps(error_result)

@mcp.tool()
async def get_service_problems(
    location: str = None,
    severity: str = None,
    state: str = None
) -> str:
    """Get list of service problems in an area (TMF656)
    
    Args:
        location: Optional location to filter by
        severity: Optional severity filter (critical, major, minor, warning, information)
        state: Optional state filter (submitted, acknowledged, inProgress, resolved, closed)
    
    Returns:
        List of service problems
    """
    await ensure_session()
    
    url = f"{FAULT_MANAGER_URL}/tmf656/serviceProblem"
    
    # Build query parameters
    params = {}
    if location:
        params["location"] = location
    if severity:
        params["severity"] = severity
    if state:
        params["state"] = state
    
    try:
        async with session.get(url, params=params, timeout=DEFAULT_TIMEOUT) as response:
            result = await response.json()
            log_audit("get_service_problems", params, result)
            return json.dumps(result, indent=2)
    except Exception as e:
        error_result = {"error": str(e)}
        log_audit("get_service_problems", params, error_result)
        return json.dumps(error_result)

# Run the server
if __name__ == "__main__":
    import atexit
    
    # Register cleanup on exit
    def cleanup():
        if session:
            asyncio.get_event_loop().run_until_complete(cleanup_session())
    
    atexit.register(cleanup)
    
    # Run FastMCP directly - it manages its own event loop
    mcp.run()
