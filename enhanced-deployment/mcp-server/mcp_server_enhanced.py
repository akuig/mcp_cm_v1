#!/usr/bin/env python3
"""
Enhanced MCP HTTP Server for Telepath AI Catalog Manager
Based on working MCP server pattern, enhanced with 8 new catalog management tools
Total: 12 tools (4 existing + 8 new)
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
mcp_server = Server("telepath-enhanced")

# Define all tools (4 existing + 8 new = 12 total)
tools = [
    # ===== EXISTING CUSTOMER-FACING TOOLS (4) =====
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
    
    # ===== NEW CATALOG MANAGEMENT TOOLS (8) =====
    Tool(
        name="list_service_specifications",
        description="List all available service specifications (TMF633) - Filter by category if needed",
        inputSchema={
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "description": "Optional category filter (e.g., 'connectivity', 'voice', 'entertainment')"
                }
            }
        }
    ),
    Tool(
        name="list_product_offerings",
        description="List all available product offerings (TMF620) - Filter by category or bundle type",
        inputSchema={
            "type": "object",
            "properties": {
                "category": {
                    "type": "string", 
                    "description": "Optional category filter (e.g., 'residential', 'business')"
                },
                "isBundle": {
                    "type": "boolean",
                    "description": "Filter for bundle vs individual offerings"
                }
            }
        }
    ),
    Tool(
        name="list_geographic_locations",
        description="List geographic locations and their service coverage (TMF673) - Check what services are available where",
        inputSchema={
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "Optional city filter (e.g., 'Springfield', 'Shelbyville')"
                },
                "serviceType": {
                    "type": "string",
                    "description": "Optional service type filter (e.g., 'broadband', 'telephony')"
                }
            }
        }
    ),
    Tool(
        name="sync_catalog_data",
        description="Synchronize and validate catalog data integrity - Check for orphaned records and data consistency",
        inputSchema={
            "type": "object",
            "properties": {
                "validateOnly": {
                    "type": "boolean",
                    "description": "If true, only validate without making changes",
                    "default": True
                },
                "fixOrphans": {
                    "type": "boolean", 
                    "description": "If true, fix orphaned references",
                    "default": False
                }
            }
        }
    ),
    Tool(
        name="create_service_specification",
        description="Create a new service specification (TMF633) - Add new service types to the catalog",
        inputSchema={
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "description": {"type": "string"},
                "category": {"type": "string"},
                "serviceType": {"type": "string"},
                "characteristics": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "valueType": {"type": "string"},
                            "defaultValue": {"type": "string"}
                        }
                    }
                }
            },
            "required": ["name", "description", "category", "serviceType"]
        }
    ),
    Tool(
        name="create_product_offering",
        description="Create a new product offering (TMF620) - Add new products that customers can purchase",
        inputSchema={
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "description": {"type": "string"},
                "category": {"type": "string"},
                "isBundle": {"type": "boolean", "default": False},
                "price": {
                    "type": "object",
                    "properties": {
                        "amount": {"type": "number"},
                        "currency": {"type": "string", "default": "USD"},
                        "period": {"type": "string", "default": "monthly"}
                    }
                }
            },
            "required": ["name", "description", "category"]
        }
    ),
    Tool(
        name="link_offering_to_specification",
        description="Link a product offering to service specifications - Connect products to the services they provide",
        inputSchema={
            "type": "object",
            "properties": {
                "productOfferingId": {"type": "string"},
                "serviceSpecificationIds": {
                    "type": "array",
                    "items": {"type": "string"}
                }
            },
            "required": ["productOfferingId", "serviceSpecificationIds"]
        }
    ),
    Tool(
        name="add_geographic_coverage",
        description="Add geographic coverage for a service specification - Extend service availability to new areas",
        inputSchema={
            "type": "object",
            "properties": {
                "serviceSpecificationId": {"type": "string"},
                "locations": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "streetName": {"type": "string"},
                            "streetNumber": {"type": "string"},
                            "city": {"type": "string"},
                            "coverage": {"type": "string", "enum": ["full", "partial", "planned"]}
                        }
                    }
                }
            },
            "required": ["serviceSpecificationId", "locations"]
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
        # ===== EXISTING TOOL HANDLERS =====
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
        
        # ===== NEW CATALOG MANAGEMENT TOOL HANDLERS =====
        elif name == "list_service_specifications":
            url = f"{CATALOG_MANAGER_URL}/tmf633/serviceSpecification"
            params = {}
            if arguments.get("category"):
                params["category"] = arguments["category"]
            async with session.get(url, params=params, timeout=DEFAULT_TIMEOUT) as response:
                result = await response.json()
                
        elif name == "list_product_offerings":
            url = f"{CATALOG_MANAGER_URL}/tmf620/productOffering"
            params = {}
            if arguments.get("category"):
                params["category"] = arguments["category"]
            if arguments.get("isBundle") is not None:
                params["isBundle"] = arguments["isBundle"]
            async with session.get(url, params=params, timeout=DEFAULT_TIMEOUT) as response:
                result = await response.json()
                
        elif name == "list_geographic_locations":
            url = f"{CATALOG_MANAGER_URL}/tmf673/geographicLocation"
            params = {}
            if arguments.get("city"):
                params["city"] = arguments["city"]
            if arguments.get("serviceType"):
                params["serviceType"] = arguments["serviceType"]
            async with session.get(url, params=params, timeout=DEFAULT_TIMEOUT) as response:
                result = await response.json()
                
        elif name == "sync_catalog_data":
            url = f"{CATALOG_MANAGER_URL}/admin/syncCatalog"
            async with session.post(url, json=arguments, timeout=DEFAULT_TIMEOUT) as response:
                result = await response.json()
                
        elif name == "create_service_specification":
            url = f"{CATALOG_MANAGER_URL}/tmf633/serviceSpecification"
            async with session.post(url, json=arguments, timeout=DEFAULT_TIMEOUT) as response:
                result = await response.json()
                
        elif name == "create_product_offering":
            url = f"{CATALOG_MANAGER_URL}/tmf620/productOffering"
            async with session.post(url, json=arguments, timeout=DEFAULT_TIMEOUT) as response:
                result = await response.json()
                
        elif name == "link_offering_to_specification":
            offering_id = arguments.get("productOfferingId")
            url = f"{CATALOG_MANAGER_URL}/admin/linkOffering/{offering_id}"
            async with session.post(url, json=arguments, timeout=DEFAULT_TIMEOUT) as response:
                result = await response.json()
                
        elif name == "add_geographic_coverage":
            spec_id = arguments.get("serviceSpecificationId")
            url = f"{CATALOG_MANAGER_URL}/admin/coverage/{spec_id}"
            async with session.post(url, json=arguments, timeout=DEFAULT_TIMEOUT) as response:
                result = await response.json()
                
        else:
            result = {"error": f"Unknown tool: {name}"}

        # Log audit trail
        audit_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "action": name,
            "arguments": arguments,
            "status": "Success" if "error" not in result else "Failed"
        }
        logger.info(f"Tool call: {json.dumps(audit_entry)}")

        return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
    except Exception as e:
        logger.error(f"Error calling tool {name}: {str(e)}")
        error_result = {"error": str(e)}
        return [TextContent(type="text", text=json.dumps(error_result))]

# HTTP endpoints
async def health(request):
    """Health check endpoint"""
    return JSONResponse({"status": "healthy", "tools": len(tools)})

async def mcp_sse_handler(request):
    """MCP Server-Sent Events handler"""
    async def event_stream():
        yield "event: ping\ndata: {}\n\n"
        
    return StreamingResponse(
        event_stream(),
        media_type="text/plain",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
    )

async def mcp_stream_handler(request):
    """MCP stream handler for JSON-RPC over HTTP"""
    try:
        body = await request.json()
        method = body.get("method")
        
        logger.info(f"MCP request: {method}")
        
        if method == "initialize":
            response = {
                "jsonrpc": "2.0",
                "id": body.get("id"),
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {"listChanged": True},
                        "resources": False,
                        "prompts": False
                    },
                    "serverInfo": {
                        "name": "telepath-enhanced",
                        "version": "2.0.0"
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
        "server_name": "telepath-enhanced",
        "capabilities": ["tools"],
        "transport": "http",
        "tools_count": len(tools)
    })

async def startup():
    """Initialize on startup"""
    logger.info(f"🚀 Starting Enhanced Telepath MCP Server on {HOST}:{PORT}")
    logger.info(f"📊 Catalog Manager: {CATALOG_MANAGER_URL}")
    logger.info(f"🛠️  Total tools available: {len(tools)}")
    logger.info(f"👥 Customer tools: service_qualification, customer_management, product_ordering, service_activation")
    logger.info(f"📋 Catalog tools: list_service_specifications, list_product_offerings, list_geographic_locations")
    logger.info(f"⚙️  Admin tools: sync_catalog_data, create_service_specification, create_product_offering")
    logger.info(f"🔗 Management tools: link_offering_to_specification, add_geographic_coverage")

async def shutdown():
    """Cleanup on shutdown"""
    global http_session
    if http_session:
        await http_session.close()

# Create Starlette app with proper endpoints
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