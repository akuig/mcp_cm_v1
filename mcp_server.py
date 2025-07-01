#!/usr/bin/env python3
"""
MCP Server for Telepath AI - Exposes TM Forum APIs as MCP tools
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime
import aiohttp
from mcp.server import Server
from mcp.types import Tool, TextContent, ToolResult, ToolCallResult

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
CATALOG_MANAGER_URL = "http://catalog-manager:8080"
DEFAULT_TIMEOUT = 30

class TelecomMCPServer:
    def __init__(self):
        self.server = Server("telepath-mcp")
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Register tools
        self.server.add_tool(self.service_qualification_tool())
        self.server.add_tool(self.customer_management_tool())
        self.server.add_tool(self.product_ordering_tool())
        self.server.add_tool(self.service_activation_tool())
        
        # Register handlers
        self.server.set_call_tool_handler(self.handle_tool_call)
        
    def service_qualification_tool(self) -> Tool:
        return Tool(
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
        )
    
    def customer_management_tool(self) -> Tool:
        return Tool(
            name="customer_management",
            description="Get customer information including account status and eligibility (TMF629)",
            inputSchema={
                "type": "object",
                "properties": {
                    "customerId": {
                        "type": "string",
                        "description": "The customer ID to look up"
                    }
                },
                "required": ["customerId"]
            }
        )
    
    def product_ordering_tool(self) -> Tool:
        return Tool(
            name="product_ordering",
            description="Create a product order for a customer (TMF622)",
            inputSchema={
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
        )
    
    def service_activation_tool(self) -> Tool:
        return Tool(
            name="service_activation",
            description="Activate a service in the network (TMF640)",
            inputSchema={
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
        )
    
    async def ensure_session(self):
        """Ensure aiohttp session is created"""
        if self.session is None:
            self.session = aiohttp.ClientSession()
    
    async def handle_tool_call(self, name: str, arguments: Any) -> List[ToolCallResult]:
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
            
            return [ToolCallResult(
                toolResult=ToolResult(
                    content=[TextContent(
                        type="text",
                        text=json.dumps(result, indent=2)
                    )]
                )
            )]
            
        except Exception as e:
            logger.error(f"Error handling tool call {name}: {str(e)}")
            return [ToolCallResult(
                toolResult=ToolResult(
                    content=[TextContent(
                        type="text",
                        text=json.dumps({"error": str(e)})
                    )]
                )
            )]
    
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
    
    async def run(self):
        """Run the MCP server"""
        try:
            async with self.server:
                logger.info("Telepath MCP Server started")
                # Keep the server running
                await asyncio.Event().wait()
        finally:
            await self.cleanup()

if __name__ == "__main__":
    server = TelecomMCPServer()
    asyncio.run(server.run())
