#!/usr/bin/env python3
"""
FIXED MCP Server for Telepath AI - Claude Compatible HTTP JSON-RPC Implementation
"""

import asyncio
import json
import logging
import os
from typing import Any, Dict, List, Optional
from datetime import datetime
import aiohttp

# HTTP server imports for Claude compatibility
from starlette.applications import Starlette
from starlette.routing import Route
from starlette.responses import JSONResponse, Response
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

class TelecomMCPServer:
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        logger.info("🚀 Telepath MCP Server initialized")

    async def ensure_session(self):
        """Ensure aiohttp session is created"""
        if self.session is None:
            self.session = aiohttp.ClientSession()

    def get_tools(self) -> List[Dict]:
        """Return list of available tools in proper MCP format"""
        tools = [
            # ===== EXISTING CUSTOMER-FACING TOOLS (4) =====
            {
                "name": "service_qualification",
                "description": "Check if a service is available at a specific location (TMF637)",
                "inputSchema": {
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
            },
            {
                "name": "customer_management",
                "description": "Get customer information including account status and eligibility (TMF629)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "customerId": {
                            "type": "string",
                            "description": "The customer ID to look up"
                        }
                    },
                    "required": ["customerId"]
                }
            },
            {
                "name": "product_ordering",
                "description": "Create a product order for a customer (TMF622)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "orderDate": {"type": "string"},
                        "externalId": {"type": "string"},
                        "customerId": {"type": "string"},
                        "productOfferingId": {"type": "string"},
                        "address": {
                            "type": "object",
                            "properties": {
                                "streetName": {"type": "string"},
                                "streetNumber": {"type": "string"},
                                "city": {"type": "string"}
                            }
                        }
                    },
                    "required": ["orderDate", "externalId", "customerId", "productOfferingId", "address"]
                }
            },
            {
                "name": "service_activation",
                "description": "Activate a service in the network (TMF640)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "serviceName": {"type": "string"},
                        "serviceType": {"type": "string"},
                        "address": {
                            "type": "object",
                            "properties": {
                                "streetName": {"type": "string"},
                                "streetNumber": {"type": "string"},
                                "city": {"type": "string"}
                            }
                        },
                        "serviceSpecificationId": {"type": "string"}
                    },
                    "required": ["serviceName", "serviceType", "address", "serviceSpecificationId"]
                }
            },
            
            # ===== NEW CATALOG MANAGEMENT TOOLS (8) =====
            {
                "name": "list_service_specifications",
                "description": "List all available service specifications (TMF633) - Filter by category if needed",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "category": {
                            "type": "string",
                            "description": "Optional category filter (e.g., 'connectivity', 'voice', 'entertainment')"
                        }
                    }
                }
            },
            {
                "name": "list_product_offerings",
                "description": "List all available product offerings (TMF620) - Filter by category or bundle type",
                "inputSchema": {
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
            },
            {
                "name": "list_geographic_locations",
                "description": "List geographic locations and their service coverage (TMF673)",
                "inputSchema": {
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
            },
            {
                "name": "sync_catalog_data",
                "description": "Synchronize and validate catalog data integrity",
                "inputSchema": {
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
            },
            {
                "name": "create_service_specification",
                "description": "Create a new service specification (TMF633)",
                "inputSchema": {
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
            },
            {
                "name": "create_product_offering",
                "description": "Create a new product offering (TMF620)",
                "inputSchema": {
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
            },
            {
                "name": "link_offering_to_specification",
                "description": "Link a product offering to service specifications",
                "inputSchema": {
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
            },
            {
                "name": "add_geographic_coverage",
                "description": "Add geographic coverage for a service specification",
                "inputSchema": {
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
            }
        ]
        
        logger.info(f"🔧 Generated {len(tools)} tools: {[tool['name'] for tool in tools]}")
        return tools

    async def route_tool_call(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Route tool calls to appropriate handlers"""
        
        logger.info(f"🔧 Routing tool call: {name}")
        logger.info(f"📋 Arguments: {arguments}")
        
        if name == "service_qualification":
            return await self.handle_service_qualification(arguments)
        elif name == "customer_management":
            return await self.handle_customer_management(arguments)
        elif name == "product_ordering":
            return await self.handle_product_ordering(arguments)
        elif name == "service_activation":
            return await self.handle_service_activation(arguments)
        elif name == "list_service_specifications":
            return await self.handle_list_service_specifications(arguments)
        elif name == "list_product_offerings":
            return await self.handle_list_product_offerings(arguments)
        elif name == "list_geographic_locations":
            return await self.handle_list_geographic_locations(arguments)
        elif name == "sync_catalog_data":
            return await self.handle_sync_catalog_data(arguments)
        elif name == "create_service_specification":
            return await self.handle_create_service_specification(arguments)
        elif name == "create_product_offering":
            return await self.handle_create_product_offering(arguments)
        elif name == "link_offering_to_specification":
            return await self.handle_link_offering_to_specification(arguments)
        elif name == "add_geographic_coverage":
            return await self.handle_add_geographic_coverage(arguments)
        else:
            return {"error": f"Unknown tool: {name}"}

    # ===== TOOL IMPLEMENTATIONS =====
    async def handle_service_qualification(self, arguments: Dict) -> Dict:
        """TMF637: Service Qualification"""
        url = f"{CATALOG_MANAGER_URL}/tmf637/serviceQualification"
        try:
            async with self.session.post(url, json=arguments, timeout=DEFAULT_TIMEOUT) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {"error": f"Service qualification failed: {response.status}"}
        except Exception as e:
            return {"error": f"Service qualification error: {str(e)}"}

    async def handle_customer_management(self, arguments: Dict) -> Dict:
        """TMF629: Customer Management"""
        customer_id = arguments.get("customerId")
        url = f"{CATALOG_MANAGER_URL}/tmf629/customer/{customer_id}"
        try:
            async with self.session.get(url, timeout=DEFAULT_TIMEOUT) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {"error": f"Customer lookup failed: {response.status}"}
        except Exception as e:
            return {"error": f"Customer management error: {str(e)}"}

    async def handle_product_ordering(self, arguments: Dict) -> Dict:
        """TMF622: Product Ordering"""
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
        try:
            async with self.session.post(url, json=order_data, timeout=DEFAULT_TIMEOUT) as response:
                if response.status in [200, 201]:
                    return await response.json()
                else:
                    return {"error": f"Product ordering failed: {response.status}"}
        except Exception as e:
            return {"error": f"Product ordering error: {str(e)}"}

    async def handle_service_activation(self, arguments: Dict) -> Dict:
        """TMF640: Service Activation"""
        url = f"{CATALOG_MANAGER_URL}/tmf640/serviceActivation"
        activation_data = {
            "service": {
                "name": arguments.get("serviceName"),
                "serviceType": arguments.get("serviceType"),
                "place": arguments.get("address"),
                "serviceSpecification": {"id": arguments.get("serviceSpecificationId")}
            }
        }
        try:
            async with self.session.post(url, json=activation_data, timeout=DEFAULT_TIMEOUT) as response:
                if response.status in [200, 201]:
                    return await response.json()
                else:
                    return {"error": f"Service activation failed: {response.status}"}
        except Exception as e:
            return {"error": f"Service activation error: {str(e)}"}

    async def handle_list_service_specifications(self, arguments: Dict) -> Dict:
        """List service specifications"""
        url = f"{CATALOG_MANAGER_URL}/tmf633/serviceSpecification"
        params = {}
        if arguments.get("category"):
            params["category"] = arguments["category"]
        try:
            async with self.session.get(url, params=params, timeout=DEFAULT_TIMEOUT) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {"error": f"Failed to list service specifications: {response.status}"}
        except Exception as e:
            return {"error": f"Service specifications error: {str(e)}"}

    async def handle_list_product_offerings(self, arguments: Dict) -> Dict:
        """List product offerings"""
        url = f"{CATALOG_MANAGER_URL}/tmf620/productOffering"
        params = {}
        if arguments.get("category"):
            params["category"] = arguments["category"]
        if arguments.get("isBundle") is not None:
            params["isBundle"] = arguments["isBundle"]
        try:
            async with self.session.get(url, params=params, timeout=DEFAULT_TIMEOUT) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {"error": f"Failed to list product offerings: {response.status}"}
        except Exception as e:
            return {"error": f"Product offerings error: {str(e)}"}

    async def handle_list_geographic_locations(self, arguments: Dict) -> Dict:
        """List geographic locations"""
        url = f"{CATALOG_MANAGER_URL}/tmf673/geographicLocation"
        params = {}
        if arguments.get("city"):
            params["city"] = arguments["city"]
        if arguments.get("serviceType"):
            params["serviceType"] = arguments["serviceType"]
        try:
            async with self.session.get(url, params=params, timeout=DEFAULT_TIMEOUT) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {"error": f"Failed to list geographic locations: {response.status}"}
        except Exception as e:
            return {"error": f"Geographic locations error: {str(e)}"}

    async def handle_sync_catalog_data(self, arguments: Dict) -> Dict:
        """Sync catalog data"""
        url = f"{CATALOG_MANAGER_URL}/admin/syncCatalog"
        try:
            async with self.session.post(url, json=arguments, timeout=DEFAULT_TIMEOUT) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {"error": f"Catalog sync failed: {response.status}"}
        except Exception as e:
            return {"error": f"Catalog sync error: {str(e)}"}

    async def handle_create_service_specification(self, arguments: Dict) -> Dict:
        """Create service specification"""
        url = f"{CATALOG_MANAGER_URL}/tmf633/serviceSpecification"
        try:
            async with self.session.post(url, json=arguments, timeout=DEFAULT_TIMEOUT) as response:
                if response.status in [200, 201]:
                    return await response.json()
                else:
                    return {"error": f"Failed to create service specification: {response.status}"}
        except Exception as e:
            return {"error": f"Create service specification error: {str(e)}"}

    async def handle_create_product_offering(self, arguments: Dict) -> Dict:
        """Create product offering"""
        url = f"{CATALOG_MANAGER_URL}/tmf620/productOffering"
        try:
            async with self.session.post(url, json=arguments, timeout=DEFAULT_TIMEOUT) as response:
                if response.status in [200, 201]:
                    return await response.json()
                else:
                    return {"error": f"Failed to create product offering: {response.status}"}
        except Exception as e:
            return {"error": f"Create product offering error: {str(e)}"}

    async def handle_link_offering_to_specification(self, arguments: Dict) -> Dict:
        """Link offering to specification"""
        offering_id = arguments.get("productOfferingId")
        url = f"{CATALOG_MANAGER_URL}/admin/linkOffering/{offering_id}"
        try:
            async with self.session.post(url, json=arguments, timeout=DEFAULT_TIMEOUT) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {"error": f"Failed to link offering to specification: {response.status}"}
        except Exception as e:
            return {"error": f"Link offering error: {str(e)}"}

    async def handle_add_geographic_coverage(self, arguments: Dict) -> Dict:
        """Add geographic coverage"""
        spec_id = arguments.get("serviceSpecificationId")
        url = f"{CATALOG_MANAGER_URL}/admin/coverage/{spec_id}"
        try:
            async with self.session.post(url, json=arguments, timeout=DEFAULT_TIMEOUT) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {"error": f"Failed to add geographic coverage: {response.status}"}
        except Exception as e:
            return {"error": f"Add coverage error: {str(e)}"}

    def log_audit(self, action: str, request: Dict, response: Dict):
        """Log audit trail for compliance"""
        audit_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "correlationId": f"{action}-{datetime.utcnow().timestamp()}",
            "action": action,
            "requestPayload": request,
            "responsePayload": response,
            "status": "Success" if "error" not in response else "Failed"
        }
        logger.info(f"📋 Audit: {json.dumps(audit_entry)}")

    async def cleanup(self):
        """Cleanup resources"""
        if self.session:
            await self.session.close()

# Global server instance
telepath_server = TelecomMCPServer()

# HTTP endpoints for Claude compatibility
async def health(request):
    """Health check endpoint"""
    return JSONResponse({
        "status": "healthy",
        "server": "telepath-claude-fixed",
        "version": "2.2.0",
        "tools_count": 12,
        "transport": "http-jsonrpc"
    })

async def mcp_stream_get_handler(request):
    """Handle GET requests to /mcp/stream - provide connection info"""
    logger.info("🔍 GET request to /mcp/stream - providing connection info")
    return JSONResponse({
        "transport": "http",
        "protocol": "json-rpc",
        "version": "2025-06-18",
        "methods": ["initialize", "tools/list", "tools/call"],
        "server": "telepath-claude-fixed",
        "status": "ready"
    })

async def mcp_stream_handler(request):
    """Enhanced MCP stream handler with Claude-compatible protocol version handling"""
    client_info = "unknown"
    try:
        body = await request.json()
        method = body.get("method")
        request_id = body.get("id")
        
        # Extract client info for better debugging
        if method == "initialize":
            client_info = body.get("params", {}).get("clientInfo", {}).get("name", "unknown")
        
        logger.info(f"🌐 HTTP MCP request from {client_info}: {method}")
        logger.info(f"📄 Request body: {json.dumps(body, indent=2)}")
        
        if method == "initialize":
            logger.info("🔧 Handling initialize request")
            # Accept Claude's protocol version and respond with compatible version
            client_version = body.get("params", {}).get("protocolVersion", "2024-11-05")
            
            # Use Claude's newer protocol version if provided
            if client_version == "2025-06-18":
                server_version = "2025-06-18"
                logger.info(f"✅ Using Claude's protocol version: {server_version}")
            else:
                server_version = "2024-11-05"
                logger.info(f"✅ Using fallback protocol version: {server_version}")
            
            response = {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "protocolVersion": server_version,
                    "capabilities": {
                        "tools": {"listChanged": True},
                        "resources": {},
                        "prompts": {}
                    },
                    "serverInfo": {
                        "name": "telepath-claude-fixed",
                        "version": "2.2.0"
                    }
                }
            }
            logger.info(f"✅ Initialize response: {json.dumps(response, indent=2)}")
            
        elif method == "tools/list":
            logger.info("📋 Handling tools/list request")
            
            # Get tools directly from the server
            tools_data = telepath_server.get_tools()
            
            response = {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "tools": tools_data
                }
            }
            
            logger.info(f"✅ Tools/list returning {len(tools_data)} tools")
            logger.info(f"🔧 Tool names: {[tool['name'] for tool in tools_data]}")
            
        elif method == "tools/call":
            logger.info("🔧 Handling tools/call request")
            params = body.get("params", {})
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            
            logger.info(f"🔧 Calling tool: {tool_name}")
            logger.info(f"📋 Tool arguments: {json.dumps(arguments, indent=2)}")
            
            # Ensure session is ready
            await telepath_server.ensure_session()
            
            # Call the tool using the server's route method
            result = await telepath_server.route_tool_call(tool_name, arguments)
            
            # Log audit trail
            telepath_server.log_audit(tool_name, arguments, result)
            
            response = {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [{"type": "text", "text": json.dumps(result, indent=2)}]
                }
            }
            
            logger.info(f"✅ Tool call completed: {tool_name}")
            
        elif method.startswith("notifications/"):
            # Handle notifications - these should NOT get responses in JSON-RPC
            logger.info(f"📢 Handling notification: {method}")
            if method == "notifications/initialized":
                logger.info("✅ Client initialization complete")
                logger.info("🕰️ Expecting tools/list request next...")
            else:
                logger.info(f"📢 Unknown notification: {method}")
            
            # Return None to indicate no response should be sent
            response = None
            
        else:
            logger.warning(f"❌ Unknown method: {method}")
            response = {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}"
                }
            }
            
        if response is not None:
            logger.info(f"📤 Response: {json.dumps(response, indent=2)}")
            return JSONResponse(response)
        else:
            logger.info("🔕 Notification acknowledged (no JSON-RPC response)")
            # For notifications, return empty response body with 200 status
            return Response(content="", status_code=200, media_type="application/json")
        
    except Exception as e:
        logger.error(f"💥 Error in HTTP JSON-RPC handler: {str(e)}")
        import traceback
        logger.error(f"💥 Full traceback: {traceback.format_exc()}")
        
        error_response = {
            "jsonrpc": "2.0",
            "id": body.get("id") if 'body' in locals() else None,
            "error": {
                "code": -32603,
                "message": f"Internal error: {str(e)}"
            }
        }
        return JSONResponse(error_response)

async def startup():
    """Initialize on startup"""
    logger.info("🌐 Starting HTTP server for Claude compatibility")
    logger.info(f"🚀 Starting CLAUDE-FIXED Telepath MCP Server on {HOST}:{PORT}")
    logger.info(f"📊 Catalog Manager: {CATALOG_MANAGER_URL}")
    logger.info("🎯 Server supports HTTP JSON-RPC transport with Claude 2025-06-18 protocol")
    
    # Log available tools on startup
    tools = telepath_server.get_tools()
    logger.info(f"🔧 Available tools on startup: {[tool['name'] for tool in tools]}")

async def shutdown():
    """Cleanup on shutdown"""
    await telepath_server.cleanup()

# Create Starlette app for HTTP transport
app = Starlette(
    routes=[
        Route("/health", health),
        Route("/mcp/stream", mcp_stream_get_handler, methods=["GET"]),
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

# Main entry point
async def main():
    """Main entry point - run HTTP server for Claude"""
    logger.info("🌐 Starting HTTP server for Claude compatibility")
    config = uvicorn.Config(app, host=HOST, port=PORT, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    asyncio.run(main())
