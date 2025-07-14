#!/usr/bin/env python3
"""
MCP Server with All 8 Tools using FastMCP HTTP Streaming
"""

import os
import logging
import json
import aiohttp
from typing import Dict, Any, Optional
from datetime import datetime
from mcp.server.fastmcp import FastMCP

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
PORT = int(os.getenv("PORT", "8090"))
HOST = os.getenv("HOST", "0.0.0.0")
CATALOG_MANAGER_URL = os.getenv("CATALOG_MANAGER_URL", "http://catalog-manager:8080")
FAULT_MANAGER_URL = os.getenv("FAULT_MANAGER_URL", "http://fault-manager:8081")
DEFAULT_TIMEOUT = 30

# Create the MCP server
mcp = FastMCP("telepath-mcp")

# Global session
session: Optional[aiohttp.ClientSession] = None

async def get_session():
    """Get or create aiohttp session"""
    global session
    if session is None:
        session = aiohttp.ClientSession()
    return session

def log_audit(action: str, request: Dict, response: Dict):
    """Log audit trail"""
    logger.info(f"Audit: {action} - Status: {'Success' if 'error' not in response else 'Failed'}")

# Original TMF tools

@mcp.tool()
async def service_qualification(
    address: Dict[str, str],
    serviceSpecification: Dict[str, str]
) -> str:
    """Check if a service is available at a specific location (TMF637)"""
    http = await get_session()
    url = f"{CATALOG_MANAGER_URL}/tmf637/serviceQualification"
    data = {"address": address, "serviceSpecification": serviceSpecification}
    
    try:
        async with http.post(url, json=data, timeout=DEFAULT_TIMEOUT) as response:
            result = await response.json()
            log_audit("service_qualification", data, result)
            return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
async def customer_management(customerId: str) -> str:
    """Get customer information including account status and eligibility (TMF629)"""
    http = await get_session()
    url = f"{CATALOG_MANAGER_URL}/tmf629/customer/{customerId}"
    
    try:
        async with http.get(url, timeout=DEFAULT_TIMEOUT) as response:
            result = await response.json()
            log_audit("customer_management", {"customerId": customerId}, result)
            return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
async def product_ordering(
    orderDate: str,
    externalId: str,
    customerId: str,
    productOfferingId: str,
    address: Dict[str, str]
) -> str:
    """Create a product order for a customer (TMF622)"""
    http = await get_session()
    url = f"{CATALOG_MANAGER_URL}/tmf622/productOrder"
    
    order_data = {
        "orderDate": orderDate,
        "externalId": externalId,
        "relatedParty": [{"id": customerId, "role": "customer"}],
        "orderItem": [{
            "action": "add",
            "productOffering": {"id": productOfferingId},
            "product": {"place": address}
        }]
    }
    
    try:
        async with http.post(url, json=order_data, timeout=DEFAULT_TIMEOUT) as response:
            result = await response.json()
            log_audit("product_ordering", order_data, result)
            return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
async def service_activation(
    serviceName: str,
    serviceType: str,
    address: Dict[str, str],
    serviceSpecificationId: str
) -> str:
    """Activate a service in the network (TMF640)"""
    http = await get_session()
    url = f"{CATALOG_MANAGER_URL}/tmf640/serviceActivation"
    
    activation_data = {
        "service": {
            "name": serviceName,
            "serviceType": serviceType,
            "place": address,
            "serviceSpecification": {"id": serviceSpecificationId}
        }
    }
    
    try:
        async with http.post(url, json=activation_data, timeout=DEFAULT_TIMEOUT) as response:
            result = await response.json()
            log_audit("service_activation", activation_data, result)
            return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})

# NEW: Fault Management tools

@mcp.tool()
async def check_service_status(
    location: Dict[str, str] = None,
    serviceId: str = None
) -> str:
    """Check service status for a location or service, detect network faults and get recommended actions"""
    http = await get_session()
    url = f"{FAULT_MANAGER_URL}/serviceStatus/check"
    data = {}
    if location:
        data["location"] = location
    if serviceId:
        data["serviceId"] = serviceId
    
    try:
        async with http.post(url, json=data, timeout=DEFAULT_TIMEOUT) as response:
            result = await response.json()
            log_audit("check_service_status", data, result)
            return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
async def create_trouble_ticket(
    description: str,
    customerId: str,
    severity: str = "minor",
    serviceId: str = None,
    contactPhone: str = None
) -> str:
    """Create a trouble ticket for customer reported issues (TMF621)"""
    http = await get_session()
    url = f"{FAULT_MANAGER_URL}/tmf621/troubleTicket"
    
    ticket_data = {
        "description": description,
        "severity": severity,
        "priority": 1 if severity in ["critical", "major"] else 3,
        "relatedParty": [{"id": customerId, "role": "customer", "name": f"Customer {customerId}"}],
        "serviceId": serviceId,
        "note": [{"text": f"Contact phone: {contactPhone}", "date": datetime.utcnow().isoformat()}] if contactPhone else []
    }
    
    try:
        async with http.post(url, json=ticket_data, timeout=DEFAULT_TIMEOUT) as response:
            result = await response.json()
            log_audit("create_trouble_ticket", ticket_data, result)
            return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
async def execute_remedial_action(
    action: str,
    faultId: str = None
) -> str:
    """Execute recommended remedial actions for network issues (REROUTE_TRAFFIC, DISPATCH_TECHNICIAN, NOTIFY_CUSTOMERS)"""
    http = await get_session()
    url = f"{FAULT_MANAGER_URL}/serviceStatus/executeAction"
    data = {"action": action}
    if faultId:
        data["faultId"] = faultId
    
    try:
        async with http.post(url, json=data, timeout=DEFAULT_TIMEOUT) as response:
            result = await response.json()
            log_audit("execute_remedial_action", data, result)
            return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
async def get_service_problems(
    location: str = None,
    severity: str = None,
    state: str = None
) -> str:
    """Get list of service problems in an area (TMF656)"""
    http = await get_session()
    url = f"{FAULT_MANAGER_URL}/tmf656/serviceProblem"
    
    params = {}
    if location:
        params["location"] = location
    if severity:
        params["severity"] = severity
    if state:
        params["state"] = state
    
    try:
        async with http.get(url, params=params, timeout=DEFAULT_TIMEOUT) as response:
            result = await response.json()
            log_audit("get_service_problems", params, result)
            return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})

# Startup message
@mcp.on("startup")
async def startup():
    logger.info(f"Starting Telepath MCP Server (FastMCP) on {HOST}:{PORT}")
    logger.info(f"Catalog Manager: {CATALOG_MANAGER_URL}")
    logger.info(f"Fault Manager: {FAULT_MANAGER_URL}")
    logger.info("Available tools: 8 (4 original + 4 fault management)")

# Cleanup on shutdown
import atexit

def cleanup():
    if session:
        import asyncio
        loop = asyncio.new_event_loop()
        loop.run_until_complete(session.close())
        loop.close()

atexit.register(cleanup)

# Run the server
if __name__ == "__main__":
    logger.info("Starting MCP server with all 8 tools...")
    # Run with streamable HTTP transport for Claude Desktop
    mcp.run(transport="streamable-http", host=HOST, port=PORT)
