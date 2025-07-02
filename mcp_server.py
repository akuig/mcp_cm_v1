#!/usr/bin/env python3
"""
MCP Server for Telepath AI - Exposes TM Forum APIs as MCP tools
Supports both HTTP streaming and SSE for Claude Desktop
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime
import aiohttp
from aiohttp import web
from aiohttp_sse import sse_response

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
CATALOG_MANAGER_URL = "http://catalog-manager:8080"
DEFAULT_TIMEOUT = 30

class TelecomMCPServer:
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.sse_clients = set()
        
    async def ensure_session(self):
        """Ensure aiohttp session is created"""
        if self.session is None:
            self.session = aiohttp.ClientSession()
    
    async def handle_tool_call(self, name: str, arguments: Any) -> Dict[str, Any]:
        """Handle tool calls and route to appropriate TMF API"""
        try:
            await self.ensure_session()
            
            if name == "service_qualification":
                result = await self.handle_service_qualification(arguments)
            elif name == "customer_management":
                result = await self.handle_customer_management(arguments)
            elif name == "product_ordering":
                result = await self.handle_product_ordering(arguments)
            elif name == "service_activation":
                result = await self.handle_service_activation(arguments)
            else:
                result = {"error": f"Unknown tool: {name}"}
            
            # Log the operation
            self.log_audit(name, arguments, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error handling tool call {name}: {str(e)}")
            return {"error": str(e)}
    
    async def handle_service_qualification(self, arguments: Dict) -> Dict:
        """TMF637: Service Qualification"""
        url = f"{CATALOG_MANAGER_URL}/tmf637/serviceQualification"
        
        async with self.session.post(url, json=arguments, timeout=DEFAULT_TIMEOUT) as response:
            return await response.json()
    
    async def handle_customer_management(self, arguments: Dict) -> Dict:
        """TMF629: Customer Management"""
        customer_id = arguments.get("customerId")
        url = f"{CATALOG_MANAGER_URL}/tmf629/customer/{customer_id}"
        
        async with self.session.get(url, timeout=DEFAULT_TIMEOUT) as response:
            return await response.json()
    
    async def handle_product_ordering(self, arguments: Dict) -> Dict:
        """TMF622: Product Ordering"""
        url = f"{CATALOG_MANAGER_URL}/tmf622/productOrder"
        
        # Transform arguments to TMF622 format
        order_data = {
            "orderDate": arguments.get("orderDate"),
            "externalId": arguments.get("externalId"),
            "relatedParty": [{
                "id": arguments.get("customerId"),
                "role": "customer"
            }],
            "orderItem": [{
                "action": "add",
                "productOffering": {
                    "id": arguments.get("productOfferingId")
                },
                "product": {
                    "place": arguments.get("address")
                }
            }]
        }
        
        async with self.session.post(url, json=order_data, timeout=DEFAULT_TIMEOUT) as response:
            return await response.json()
    
    async def handle_service_activation(self, arguments: Dict) -> Dict:
        """TMF640: Service Activation"""
        url = f"{CATALOG_MANAGER_URL}/tmf640/serviceActivation"
        
        # Transform arguments to TMF640 format
        activation_data = {
            "service": {
                "name": arguments.get("serviceName"),
                "serviceType": arguments.get("serviceType"),
                "place": arguments.get("address"),
                "serviceSpecification": {
                    "id": arguments.get("serviceSpecificationId")
                }
            }
        }
        
        async with self.session.post(url, json=activation_data, timeout=DEFAULT_TIMEOUT) as response:
            return await response.json()
    
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
        logger.info(f"Audit: {json.dumps(audit_entry)}")
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.session:
            await self.session.close()
    
    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """Get tool definitions for the MCP protocol"""
        return [
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
            }
        ]
    
    async def handle_sse(self, request):
        """Handle Server-Sent Events for Claude Desktop"""
        logger.info("SSE connection established")
        
        async with sse_response(request) as resp:
            self.sse_clients.add(resp)
            try:
                # Keep connection alive
                while True:
                    await asyncio.sleep(30)
                    await resp.send(json.dumps({"type": "ping"}))
            except Exception as e:
                logger.error(f"SSE error: {e}")
            finally:
                self.sse_clients.discard(resp)
        
        return resp
    
    async def handle_message(self, request):
        """Handle POST messages and send responses via SSE"""
        try:
            data = await request.json()
            logger.info(f"Received request: {data}")
            
            method = data.get('method', '')
            params = data.get('params', {})
            request_id = data.get('id')
            
            # Handle notifications (no response needed)
            if method.startswith('notifications/'):
                logger.info(f"Received notification: {method}")
                return web.Response(status=200)
            
            # Process the request
            result = await self.process_method(method, params)
            
            # Create response
            response_data = {
                "jsonrpc": "2.0",
                "result": result
            }
            
            if request_id is not None:
                response_data["id"] = request_id
            
            # Send response to all SSE clients
            for client in self.sse_clients:
                try:
                    await client.send(json.dumps(response_data))
                except Exception as e:
                    logger.error(f"Failed to send to SSE client: {e}")
            
            return web.Response(status=200)
            
        except Exception as e:
            logger.error(f"Message handling error: {str(e)}")
            return web.Response(status=500, text=str(e))
    
    async def process_method(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Process MCP protocol methods"""
        if method == 'initialize':
            # Extract protocol version from params
            protocol_version = params.get('protocolVersion', '1.0')
            client_info = params.get('clientInfo', {})
            
            logger.info(f"Client: {client_info.get('name')} v{client_info.get('version')} using protocol {protocol_version}")
            
            return {
                "protocolVersion": protocol_version,
                "capabilities": {
                    "tools": {}
                },
                "serverInfo": {
                    "name": "telepath-mcp",
                    "version": "1.0.0"
                }
            }
        
        elif method == 'tools/list':
            return {"tools": self.get_tool_definitions()}
        
        elif method == 'tools/call':
            tool_name = params.get('name')
            tool_args = params.get('arguments', {})
            
            tool_result = await self.handle_tool_call(tool_name, tool_args)
            
            return {
                "content": [{"type": "text", "text": json.dumps(tool_result, indent=2)}],
                "isError": False
            }
        
        else:
            return {"error": f"Unknown method: {method}"}
    
    async def handle_stream(self, request):
        """Handle streaming HTTP requests (for non-SSE clients)"""
        response = web.StreamResponse(
            status=200,
            headers={
                'Content-Type': 'application/json-stream',
                'Transfer-Encoding': 'chunked',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Cache-Control': 'no-cache',
            }
        )
        await response.prepare(request)
        
        try:
            data = await request.json()
            method = data.get('method', '')
            params = data.get('params', {})
            request_id = data.get('id')
            
            # Handle notifications
            if method.startswith('notifications/'):
                logger.info(f"Received notification: {method}")
                # Send empty response for notifications
                response_data = {
                    "jsonrpc": "2.0",
                    "result": {},
                    "id": request_id
                }
            else:
                # Process the request
                result = await self.process_method(method, params)
                
                response_data = {
                    "jsonrpc": "2.0",
                    "result": result,
                    "id": request_id
                }
            
            # Write response as a chunk
            await response.write(json.dumps(response_data).encode('utf-8'))
            await response.write(b'\n')
            
        except Exception as e:
            logger.error(f"Stream error: {str(e)}")
            error_response = {
                "jsonrpc": "2.0",
                "error": {
                    "code": -32603,
                    "message": str(e)
                },
                "id": request_id if 'request_id' in locals() else None
            }
            await response.write(json.dumps(error_response).encode('utf-8'))
            await response.write(b'\n')
        
        finally:
            await response.write_eof()
        
        return response
    
    async def handle_options(self, request):
        """Handle CORS preflight requests"""
        return web.Response(
            headers={
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type',
            }
        )
    
    async def health_check(self, request):
        """Health check endpoint"""
        return web.json_response({"status": "healthy", "service": "mcp-server"})
    
    async def run(self):
        """Run the MCP server with both SSE and HTTP streaming support"""
        app = web.Application()
        
        # SSE endpoints for Claude Desktop
        app.router.add_get('/sse', self.handle_sse)
        app.router.add_post('/sse', self.handle_message)
        
        # Streaming endpoints
        app.router.add_post('/mcp/stream', self.handle_stream)
        app.router.add_options('/mcp/stream', self.handle_options)
        
        # Legacy endpoints
        app.router.add_post('/messages', self.handle_stream)
        app.router.add_options('/messages', self.handle_options)
        
        # Health check
        app.router.add_get('/health', self.health_check)
        
        try:
            runner = web.AppRunner(app)
            await runner.setup()
            site = web.TCPSite(runner, '0.0.0.0', 8090)
            await site.start()
            
            logger.info("Telepath MCP Server started on http://0.0.0.0:8090")
            logger.info("SSE endpoint: http://0.0.0.0:8090/sse")
            logger.info("Streaming endpoint: http://0.0.0.0:8090/mcp/stream")
            logger.info("Health check: http://0.0.0.0:8090/health")
            
            # Keep the server running
            await asyncio.Event().wait()
        finally:
            await self.cleanup()
            await runner.cleanup()

if __name__ == "__main__":
    server = TelecomMCPServer()
    asyncio.run(server.run())
