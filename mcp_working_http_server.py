#!/usr/bin/env python3
"""
Working MCP HTTP Server for Claude Desktop
Uses the correct MCP SDK patterns
"""

import os
import json
import logging
import aiohttp
from typing import Dict, Any, Optional
from datetime import datetime
import asyncio
from mcp.server.models import InitializationOptions
from mcp.server import Server
from mcp.types import Tool, TextContent
from starlette.applications import Starlette
from starlette.routing import Route
from starlette.responses import JSONResponse, StreamingResponse
from starlette.middleware.cors import CORSMiddleware
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
mcp_server = Server("telepath-mcp")

# Define tools
tools = [
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
    )
]

# Register handlers
@mcp_server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """Return list of available tools"""
    return tools

@mcp_server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls"""
    session = await get_http_session()
    
    try:
        if name == "service_qualification":
            url = f"{CATALOG_MANAGER_URL}/tmf637/serviceQualification"
            async with session.post(url, json=arguments, timeout=DEFAULT_TIMEOUT) as response:
                result = await response.json()
                
        elif name == "customer_management":
            customer_id = arguments.get("customerId")
            url = f"{CATALOG_MANAGER_URL}/tmf629/customer/{customer_id}"
            async with session.get(url, timeout=DEFAULT_TIMEOUT) as response:
                result = await response.json()
                
        elif name == "product_ordering":
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
                
        elif name == "service_activation":
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
                
        elif name == "check_service_status":
            url = f"{FAULT_MANAGER_URL}/serviceStatus/check"
            data = {}
            if arguments.get("location"):
                data["location"] = arguments["location"]
            if arguments.get("serviceId"):
                data["serviceId"] = arguments["serviceId"]
            async with session.post(url, json=data, timeout=DEFAULT_TIMEOUT) as response:
                result = await response.json()
                
        elif name == "create_trouble_ticket":
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
                
        elif name == "execute_remedial_action":
            url = f"{FAULT_MANAGER_URL}/serviceStatus/executeAction"
            data = {"action": arguments.get("action")}
            if arguments.get("faultId"):
                data["faultId"] = arguments["faultId"]
            async with session.post(url, json=data, timeout=DEFAULT_TIMEOUT) as response:
                result = await response.json()
                
        elif name == "get_service_problems":
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
        else:
            result = {"error": f"Unknown tool: {name}"}
            
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
    except Exception as e:
        logger.error(f"Error calling tool {name}: {str(e)}")
        return [TextContent(type="text", text=json.dumps({"error": str(e)}))]

# Create HTTP endpoints
async def health(request):
    """Health check endpoint"""
    return JSONResponse({
        "status": "healthy",
        "server": "telepath-mcp",
        "transport": "http",
        "tools": len(tools)
    })

async def mcp_sse_handler(request):
    """Handle SSE connections"""
    async def event_generator():
        yield "data: {\"type\": \"connection\", \"status\": \"connected\"}\n\n"
        # Keep connection alive
        while True:
            await asyncio.sleep(30)
            yield "data: {\"type\": \"ping\"}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )

async def mcp_stream_handler(request):
    """Handle MCP streaming requests"""
    try:
        body = await request.json()
        method = body.get("method", "")
        
        if method == "initialize":
            response = {
                "jsonrpc": "2.0",
                "id": body.get("id"),
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": True,
                        "resources": False,
                        "prompts": False
                    },
                    "serverInfo": {
                        "name": "telepath-mcp",
                        "version": "1.0.0"
                    }
                }
            }
        elif method == "tools/list":
            response = {
                "jsonrpc": "2.0",
                "id": body.get("id"),
                "result": {
                    "tools": [tool.dict() for tool in tools]
                }
            }
        elif method == "tools/call":
            tool_name = body.get("params", {}).get("name")
            arguments = body.get("params", {}).get("arguments", {})
            
            # Call the tool handler
            results = await handle_call_tool(tool_name, arguments)
            
            response = {
                "jsonrpc": "2.0",
                "id": body.get("id"),
                "result": {
                    "content": [{"type": "text", "text": results[0].text}]
                }
            }
        else:
            response = {
                "jsonrpc": "2.0",
                "id": body.get("id"),
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}"
                }
            }
            
        return JSONResponse(response)
        
    except Exception as e:
        logger.error(f"Error in stream handler: {str(e)}")
        return JSONResponse({
            "jsonrpc": "2.0",
            "id": body.get("id") if 'body' in locals() else None,
            "error": {
                "code": -32603,
                "message": f"Internal error: {str(e)}"
            }
        })

async def mcp_info_handler(request):
    """MCP info endpoint"""
    return JSONResponse({
        "mcp_version": "2024-11-05",
        "server_name": "telepath-mcp",
        "capabilities": ["tools"],
        "transport": "http"
    })

async def startup():
    """Initialize on startup"""
    logger.info(f"Starting Telepath MCP Server on {HOST}:{PORT}")
    logger.info(f"Catalog Manager: {CATALOG_MANAGER_URL}")
    logger.info(f"Fault Manager: {FAULT_MANAGER_URL}")
    logger.info(f"Available tools: {len(tools)}")

async def shutdown():
    """Cleanup on shutdown"""
    global http_session
    if http_session:
        await http_session.close()

# Create Starlette app
app = Starlette(
    routes=[
        Route("/health", health),
        Route("/mcp", mcp_info_handler),
        Route("/mcp/sse", mcp_sse_handler),
        Route("/mcp/stream", mcp_stream_handler, methods=["POST"]),
    ],
    on_startup=[startup],
    on_shutdown=[shutdown]
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Run the server
if __name__ == "__main__":
    uvicorn.run(app, host=HOST, port=PORT)
