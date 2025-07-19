#!/usr/bin/env python3
"""
MCP SPEC COMPLIANT Server - Try exact specification format
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
        logger.info("🚀 MCP Spec Compliant Server initialized")

    async def ensure_session(self):
        """Ensure aiohttp session is created"""
        if self.session is None:
            self.session = aiohttp.ClientSession()

    def get_tools(self) -> List[Dict]:
        """Return tools in exact MCP specification format"""
        tools = [
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
        else:
            return {"error": f"Unknown tool: {name}"}

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
        "server": "telepath-spec-compliant",
        "version": "2.5.0",
        "tools_count": 1,
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
        "server": "telepath-spec-compliant",
        "status": "ready"
    })

async def mcp_stream_handler(request):
    """MCP stream handler - try exact specification compliance"""
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
            # Accept Claude's protocol version
            client_version = body.get("params", {}).get("protocolVersion", "2024-11-05")
            
            # Try EXACT MCP spec format
            if client_version == "2025-06-18":
                server_version = "2025-06-18"
                logger.info(f"✅ Using Claude's protocol version: {server_version}")
            else:
                server_version = "2024-11-05"
                logger.info(f"✅ Using fallback protocol version: {server_version}")
            
            # Try complete capabilities structure
            response = {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "protocolVersion": server_version,
                    "capabilities": {
                        "tools": {
                            "listChanged": True
                        },
                        "resources": {
                            "subscribe": False,
                            "listChanged": False  
                        },
                        "prompts": {
                            "listChanged": False
                        },
                        "logging": {},
                        "completion": {
                            "argument": False
                        }
                    },
                    "serverInfo": {
                        "name": "telepath-spec-compliant",
                        "version": "2.5.0"
                    },
                    "instructions": None
                }
            }
            logger.info(f"✅ Initialize response: {json.dumps(response, indent=2)}")
            
        elif method == "tools/list":
            logger.info("📋 🎉 SUCCESS! CLAUDE REQUESTED TOOLS LIST! 🎉")
            
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
            
            logger.info(f"🔧 🎉 CLAUDE CALLED TOOL: {tool_name} 🎉")
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
    logger.info(f"🚀 Starting MCP SPEC COMPLIANT Server on {HOST}:{PORT}")
    logger.info(f"📊 Catalog Manager: {CATALOG_MANAGER_URL}")
    logger.info("🎯 Server uses complete MCP capabilities structure")
    
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
