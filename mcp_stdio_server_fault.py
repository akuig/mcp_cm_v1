#!/usr/bin/env python3
"""
MCP Server for Claude Desktop - STDIO Transport with Fault Management
"""

import os
import logging
import json
import asyncio
import aiohttp
from typing import Dict, Any
from datetime import datetime
from mcp.server import Server
from mcp.types import Tool, TextContent

# Configure logging to stderr so it doesn't interfere with stdio
import sys
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)

# Configuration
CATALOG_MANAGER_URL = os.getenv("CATALOG_MANAGER_URL", "http://localhost:8080")
FAULT_MANAGER_URL = os.getenv("FAULT_MANAGER_URL", "http://localhost:8081")
DEFAULT_TIMEOUT = 30

class TelecomMCPServer:
    def __init__(self):
        self.server = Server("telepath-mcp")
        self.session = None
        
        # Register tools
        self._register_tools()
        
        # Set up handlers
        self.server.request_handlers["tools/call"] = self.handle_tool_call
        
    def _register_tools(self):
        """Register all available tools"""
        # Original TMF tools
        self.server.list_tools_handler = lambda: [
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
                description="Get customer information including account status and eligibility (TMF629)",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "customerId": {"type": "string", "description": "The customer ID to look up"}
                    },
                    "required": ["customerId"]
                }
            ),
            Tool(
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
            ),
            Tool(
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
            ),
            # Fault Management tools
            Tool(
                name="check_service_status",
                description="Check service status for a location or service, detect network faults and get recommended actions",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "object",
                            "properties": {
                                "streetName": {"type": "string"},
                                "streetNumber": {"type": "string"},
                                "city": {"type": "string"}
                            }
                        },
                        "serviceId": {"type": "string", "description": "Optional service ID to check"}
                    }
                }
            ),
            Tool(
                name="create_trouble_ticket",
                description="Create a trouble ticket for customer reported issues (TMF621)",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "description": {"type": "string"},
                        "customerId": {"type": "string"},
                        "severity": {
                            "type": "string",
                            "enum": ["critical", "major", "minor", "warning", "information"]
                        },
                        "serviceId": {"type": "string"},
                        "contactPhone": {"type": "string"}
                    },
                    "required": ["description", "customerId"]
                }
            ),
            Tool(
                name="execute_remedial_action",
                description="Execute recommended remedial actions for network issues",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["REROUTE_TRAFFIC", "DISPATCH_TECHNICIAN", "NOTIFY_CUSTOMERS"]
                        },
                        "faultId": {"type": "string", "description": "Optional fault ID"}
                    },
                    "required": ["action"]
                }
            ),
            Tool(
                name="get_service_problems",
                description="Get list of service problems in an area (TMF656)",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "location": {"type": "string"},
                        "severity": {
                            "type": "string",
                            "enum": ["critical", "major", "minor", "warning", "information"]
                        },
                        "state": {
                            "type": "string",
                            "enum": ["submitted", "acknowledged", "inProgress", "resolved", "closed"]
                        }
                    }
                }
            )
        ]
    
    async def ensure_session(self):
        """Ensure aiohttp session is created"""
        if self.session is None:
            self.session = aiohttp.ClientSession()
    
    async def handle_tool_call(self, name: str, arguments: dict) -> list:
        """Handle tool calls"""
        await self.ensure_session()
        
        try:
            if name == "service_qualification":
                result = await self._service_qualification(arguments)
            elif name == "customer_management":
                result = await self._customer_management(arguments)
            elif name == "product_ordering":
                result = await self._product_ordering(arguments)
            elif name == "service_activation":
                result = await self._service_activation(arguments)
            elif name == "check_service_status":
                result = await self._check_service_status(arguments)
            elif name == "create_trouble_ticket":
                result = await self._create_trouble_ticket(arguments)
            elif name == "execute_remedial_action":
                result = await self._execute_remedial_action(arguments)
            elif name == "get_service_problems":
                result = await self._get_service_problems(arguments)
            else:
                result = {"error": f"Unknown tool: {name}"}
            
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
            
        except Exception as e:
            logger.error(f"Error handling tool {name}: {str(e)}")
            return [TextContent(type="text", text=json.dumps({"error": str(e)}))]
    
    # Tool implementations
    async def _service_qualification(self, args: dict) -> dict:
        """TMF637: Service Qualification"""
        url = f"{CATALOG_MANAGER_URL}/tmf637/serviceQualification"
        async with self.session.post(url, json=args, timeout=DEFAULT_TIMEOUT) as response:
            return await response.json()
    
    async def _customer_management(self, args: dict) -> dict:
        """TMF629: Customer Management"""
        customer_id = args.get("customerId")
        url = f"{CATALOG_MANAGER_URL}/tmf629/customer/{customer_id}"
        async with self.session.get(url, timeout=DEFAULT_TIMEOUT) as response:
            return await response.json()
    
    async def _product_ordering(self, args: dict) -> dict:
        """TMF622: Product Ordering"""
        url = f"{CATALOG_MANAGER_URL}/tmf622/productOrder"
        order_data = {
            "orderDate": args.get("orderDate"),
            "externalId": args.get("externalId"),
            "relatedParty": [{"id": args.get("customerId"), "role": "customer"}],
            "orderItem": [{
                "action": "add",
                "productOffering": {"id": args.get("productOfferingId")},
                "product": {"place": args.get("address")}
            }]
        }
        async with self.session.post(url, json=order_data, timeout=DEFAULT_TIMEOUT) as response:
            return await response.json()
    
    async def _service_activation(self, args: dict) -> dict:
        """TMF640: Service Activation"""
        url = f"{CATALOG_MANAGER_URL}/tmf640/serviceActivation"
        activation_data = {
            "service": {
                "name": args.get("serviceName"),
                "serviceType": args.get("serviceType"),
                "place": args.get("address"),
                "serviceSpecification": {"id": args.get("serviceSpecificationId")}
            }
        }
        async with self.session.post(url, json=activation_data, timeout=DEFAULT_TIMEOUT) as response:
            return await response.json()
    
    async def _check_service_status(self, args: dict) -> dict:
        """Check service status"""
        url = f"{FAULT_MANAGER_URL}/serviceStatus/check"
        data = {}
        if args.get("location"):
            data["location"] = args["location"]
        if args.get("serviceId"):
            data["serviceId"] = args["serviceId"]
        async with self.session.post(url, json=data, timeout=DEFAULT_TIMEOUT) as response:
            return await response.json()
    
    async def _create_trouble_ticket(self, args: dict) -> dict:
        """TMF621: Create trouble ticket"""
        url = f"{FAULT_MANAGER_URL}/tmf621/troubleTicket"
        ticket_data = {
            "description": args.get("description"),
            "severity": args.get("severity", "minor"),
            "priority": 1 if args.get("severity") in ["critical", "major"] else 3,
            "relatedParty": [{
                "id": args.get("customerId"),
                "role": "customer",
                "name": f"Customer {args.get('customerId')}"
            }],
            "serviceId": args.get("serviceId"),
            "note": [{
                "text": f"Contact phone: {args.get('contactPhone')}",
                "date": datetime.utcnow().isoformat()
            }] if args.get("contactPhone") else []
        }
        async with self.session.post(url, json=ticket_data, timeout=DEFAULT_TIMEOUT) as response:
            return await response.json()
    
    async def _execute_remedial_action(self, args: dict) -> dict:
        """Execute remedial action"""
        url = f"{FAULT_MANAGER_URL}/serviceStatus/executeAction"
        data = {"action": args.get("action")}
        if args.get("faultId"):
            data["faultId"] = args["faultId"]
        async with self.session.post(url, json=data, timeout=DEFAULT_TIMEOUT) as response:
            return await response.json()
    
    async def _get_service_problems(self, args: dict) -> dict:
        """TMF656: Get service problems"""
        url = f"{FAULT_MANAGER_URL}/tmf656/serviceProblem"
        params = {}
        if args.get("location"):
            params["location"] = args["location"]
        if args.get("severity"):
            params["severity"] = args["severity"]
        if args.get("state"):
            params["state"] = args["state"]
        async with self.session.get(url, params=params, timeout=DEFAULT_TIMEOUT) as response:
            return await response.json()
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.session:
            await self.session.close()
    
    async def run(self):
        """Run the MCP server"""
        logger.info("Starting Telepath MCP Server (STDIO mode)")
        logger.info(f"Catalog Manager: {CATALOG_MANAGER_URL}")
        logger.info(f"Fault Manager: {FAULT_MANAGER_URL}")
        
        # Run with stdio transport
        from mcp.server.stdio import stdio_server
        
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )

async def main():
    server = TelecomMCPServer()
    try:
        await server.run()
    finally:
        await server.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
