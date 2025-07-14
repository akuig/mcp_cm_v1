#!/usr/bin/env python3
"""
Simple MCP HTTP Server for Claude Desktop using MCP SDK directly
"""

import os
import json
import logging
import aiohttp
from typing import Dict, Any, Optional
from datetime import datetime
from mcp import ServerSession, Tool
from mcp.server import Server
from mcp.types import TextContent, Resource, Prompt
from starlette.applications import Starlette
from starlette.routing import Route
from starlette.responses import JSONResponse, StreamingResponse
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
PORT = int(os.getenv("PORT", "8090"))
HOST = os.getenv("HOST", "0.0.0.0")
CATALOG_MANAGER_URL = os.getenv("CATALOG_MANAGER_URL", "http://catalog-manager:8080")
FAULT_MANAGER_URL = os.getenv("FAULT_MANAGER_URL", "http://fault-manager:8081")
DEFAULT_TIMEOUT = 30

# Global session
http_session: Optional[aiohttp.ClientSession] = None

async def get_http_session():
    """Get or create aiohttp session"""
    global http_session
    if http_session is None:
        http_session = aiohttp.ClientSession()
    return http_session

# Create MCP server
server = Server("telepath-mcp")

# Tool implementations
async def service_qualification_handler(arguments: dict) -> list:
    """TMF637: Service Qualification"""
    session = await get_http_session()
    url = f"{CATALOG_MANAGER_URL}/tmf637/serviceQualification"
    async with session.post(url, json=arguments, timeout=DEFAULT_TIMEOUT) as response:
        result = await response.json()
        return [TextContent(type="text", text=json.dumps(result, indent=2))]

async def customer_management_handler(arguments: dict) -> list:
    """TMF629: Customer Management"""
    session = await get_http_session()
    customer_id = arguments.get("customerId")
    url = f"{CATALOG_MANAGER_URL}/tmf629/customer/{customer_id}"
    async with session.get(url, timeout=DEFAULT_TIMEOUT) as response:
        result = await response.json()
        return [TextContent(type="text", text=json.dumps(result, indent=2))]

async def product_ordering_handler(arguments: dict) -> list:
    """TMF622: Product Ordering"""
    session = await get_http_session()
    url = f"{CATALOG_MANAGER_URL}/tmf622/productOrder"
    order_data = {
        "orderDate": arguments.get("orderDate"),
        "externalId": arguments.get("externalId"),
        "relatedParty": [{"id": arguments.get("customerId"), "role": "customer"}],
        "orderItem": [{
            "action": "add",
            "productOffering": {"id": arguments.get("productOfferingId")},
            "product": {"place": arguments.get("address")}
        }]
    }
    async with session.post(url, json=order_data, timeout=DEFAULT_TIMEOUT) as response:
        result = await response.json()
        return [TextContent(type="text", text=json.dumps(result, indent=2))]

async def service_activation_handler(arguments: dict) -> list:
    """TMF640: Service Activation"""
    session = await get_http_session()
    url = f"{CATALOG_MANAGER_URL}/tmf640/serviceActivation"
    activation_data = {
        "service": {
            "name": arguments.get("serviceName"),
            "serviceType": arguments.get("serviceType"),
            "place": arguments.get("address"),
            "serviceSpecification": {"id": arguments.get("serviceSpecificationId")}
        }
    }
    async with session.post(url, json=activation_data, timeout=DEFAULT_TIMEOUT) as response:
        result = await response.json()
        return [TextContent(type="text", text=json.dumps(result, indent=2))]

async def check_service_status_handler(arguments: dict) -> list:
    """Check service status"""
    session = await get_http_session()
    url = f"{FAULT_MANAGER_URL}/serviceStatus/check"
    data = {}
    if arguments.get("location"):
        data["location"] = arguments["location"]
    if arguments.get("serviceId"):
        data["serviceId"] = arguments["serviceId"]
    async with session.post(url, json=data, timeout=DEFAULT_TIMEOUT) as response:
        result = await response.json()
        return [TextContent(type="text", text=json.dumps(result, indent=2))]

async def create_trouble_ticket_handler(arguments: dict) -> list:
    """TMF621: Create trouble ticket"""
    session = await get_http_session()
    url = f"{FAULT_MANAGER_URL}/tmf621/troubleTicket"
    ticket_data = {
        "description": arguments.get("description"),
        "severity": arguments.get("severity", "minor"),
        "priority": 1 if arguments.get("severity") in ["critical", "major"] else 3,
        "relatedParty": [{
            "id": arguments.get("customerId"),
            "role": "customer",
            "name": f"Customer {arguments.get('customerId')}"
        }],
        "serviceId": arguments.get("serviceId"),
        "note": [{
            "text": f"Contact phone: {arguments.get('contactPhone')}",
            "date": datetime.utcnow().isoformat()
        }] if arguments.get("contactPhone") else []
    }
    async with session.post(url, json=ticket_data, timeout=DEFAULT_TIMEOUT) as response:
        result = await response.json()
        return [TextContent(type="text", text=json.dumps(result, indent=2))]

async def execute_remedial_action_handler(arguments: dict) -> list:
    """Execute remedial action"""
    session = await get_http_session()
    url = f"{FAULT_MANAGER_URL}/serviceStatus/executeAction"
    data = {"action": arguments.get("action")}
    if arguments.get("faultId"):
        data["faultId"] = arguments["faultId"]
    async with session.post(url, json=data, timeout=DEFAULT_TIMEOUT) as response:
        result = await response.json()
        return [TextContent(type="text", text=json.dumps(result, indent=2))]

async def get_service_problems_handler(arguments: dict) -> list:
    """TMF656: Get service problems"""
    session = await get_http_session()
    url = f"{FAULT_MANAGER_URL}/tmf656/serviceProblem"
    params = {}
    if arguments.get("location"):
        params["location"] = arguments["location"]
    if arguments.get("severity"):
        params["severity"] = arguments["severity"]
    if arguments.get("state"):
        params["state"] = arguments["state"]
    async with session.get(url, params=params, timeout=DEFAULT_TIMEOUT) as response:
        result = await response.json()
        return [TextContent(type="text", text=json.dumps(result, indent=2))]

# Register tools
server.add_tool(
    Tool(
        name="service_qualification",
        description="Check if a service is available at a specific location (TMF637)",
        inputSchema={
            "type": "object",
            "properties": {
                "address": {
                    "type": "object",
                    "properties": {
                        "streetName": {"type": "string"},
                        "streetNumber": {"type": "string"},
                        "city": {"type": "string"}
                    },
                    "required": ["streetName", "streetNumber", "city"]
                },
                "serviceSpecification": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "name": {"type": "string"}
                    },
                    "required": ["id", "name"]
                }
            },
            "required": ["address", "serviceSpecification"]
        }
    ),
    service_qualification_handler
)

server.add_tool(
    Tool(
        name="customer_management",
        description="Get customer information (TMF629)",
        inputSchema={
            "type": "object",
            "properties": {
                "customerId": {"type": "string"}
            },
            "required": ["customerId"]
        }
    ),
    customer_management_handler
)

server.add_tool(
    Tool(
        name="product_ordering",
        description="Create a product order (TMF622)",
        inputSchema={
            "type": "object",
            "properties": {
                "orderDate": {"type": "string"},
                "externalId": {"type": "string"},
                "customerId": {"type": "string"},
                "productOfferingId": {"type": "string"},
                "address": {"type": "object"}
            },
            "required": ["orderDate", "externalId", "customerId", "productOfferingId", "address"]
        }
    ),
    product_ordering_handler
)

server.add_tool(
    Tool(
        name="service_activation",
        description="Activate a service (TMF640)",
        inputSchema={
            "type": "object",
            "properties": {
                "serviceName": {"type": "string"},
                "serviceType": {"type": "string"},
                "address": {"type": "object"},
                "serviceSpecificationId": {"type": "string"}
            },
            "required": ["serviceName", "serviceType", "address", "serviceSpecificationId"]
        }
    ),
    service_activation_handler
)

server.add_tool(
    Tool(
        name="check_service_status",
        description="Check service status for network faults",
        inputSchema={
            "type": "object",
            "properties": {
                "location": {"type": "object"},
                "serviceId": {"type": "string"}
            }
        }
    ),
    check_service_status_handler
)

server.add_tool(
    Tool(
        name="create_trouble_ticket",
        description="Create trouble ticket (TMF621)",
        inputSchema={
            "type": "object",
            "properties": {
                "description": {"type": "string"},
                "customerId": {"type": "string"},
                "severity": {"type": "string"},
                "serviceId": {"type": "string"},
                "contactPhone": {"type": "string"}
            },
            "required": ["description", "customerId"]
        }
    ),
    create_trouble_ticket_handler
)

server.add_tool(
    Tool(
        name="execute_remedial_action",
        description="Execute remedial actions",
        inputSchema={
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["REROUTE_TRAFFIC", "DISPATCH_TECHNICIAN", "NOTIFY_CUSTOMERS"]
                },
                "faultId": {"type": "string"}
            },
            "required": ["action"]
        }
    ),
    execute_remedial_action_handler
)

server.add_tool(
    Tool(
        name="get_service_problems",
        description="Get service problems (TMF656)",
        inputSchema={
            "type": "object",
            "properties": {
                "location": {"type": "string"},
                "severity": {"type": "string"},
                "state": {"type": "string"}
            }
        }
    ),
    get_service_problems_handler
)

# Create HTTP endpoints
async def health(request):
    """Health check endpoint"""
    return JSONResponse({
        "status": "healthy",
        "server": "telepath-mcp",
        "transport": "http"
    })

async def mcp_handler(request):
    """Handle MCP requests"""
    # This is a simplified handler - in production you'd implement
    # the full MCP protocol handling here
    return JSONResponse({
        "name": "telepath-mcp",
        "version": "1.0.0",
        "protocol_version": "2024-11-05"
    })

async def startup():
    """Initialize on startup"""
    logger.info(f"Starting Telepath MCP Server on {HOST}:{PORT}")
    logger.info(f"Catalog Manager: {CATALOG_MANAGER_URL}")
    logger.info(f"Fault Manager: {FAULT_MANAGER_URL}")

async def shutdown():
    """Cleanup on shutdown"""
    global http_session
    if http_session:
        await http_session.close()

# Create Starlette app
app = Starlette(
    routes=[
        Route("/health", health),
        Route("/mcp", mcp_handler),
        Route("/mcp/{path:path}", mcp_handler, methods=["GET", "POST"]),
    ],
    on_startup=[startup],
    on_shutdown=[shutdown]
)

# Run the server
if __name__ == "__main__":
    uvicorn.run(app, host=HOST, port=PORT)
