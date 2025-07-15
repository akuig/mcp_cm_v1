#!/usr/bin/env python3
"""
MCP Server for Telepath AI - Exposes TM Forum APIs as MCP tools
Enhanced with Catalog Management capabilities
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
        
        # Register existing customer-facing tools
        self.server.add_tool(self.service_qualification_tool())
        self.server.add_tool(self.customer_management_tool())
        self.server.add_tool(self.product_ordering_tool())
        self.server.add_tool(self.service_activation_tool())
        
        # Register new catalog management tools
        self.server.add_tool(self.list_service_specifications_tool())
        self.server.add_tool(self.list_product_offerings_tool())
        self.server.add_tool(self.list_geographic_locations_tool())
        self.server.add_tool(self.sync_catalog_data_tool())
        self.server.add_tool(self.create_service_specification_tool())
        self.server.add_tool(self.create_product_offering_tool())
        self.server.add_tool(self.link_offering_to_specification_tool())
        self.server.add_tool(self.add_geographic_coverage_tool())
        
        # Register handlers
        self.server.set_call_tool_handler(self.handle_tool_call)
    
    # ===== EXISTING CUSTOMER-FACING TOOLS =====
    
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
    
    # ===== NEW CATALOG MANAGEMENT TOOLS =====
    
    def list_service_specifications_tool(self) -> Tool:
        return Tool(
            name="list_service_specifications",
            description="List all available service specifications (TMF633)",
            inputSchema={
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": "Optional category filter (e.g., 'connectivity', 'voice', 'data')"
                    }
                }
            }
        )
    
    def list_product_offerings_tool(self) -> Tool:
        return Tool(
            name="list_product_offerings",
            description="List all available product offerings (TMF620)",
            inputSchema={
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string", 
                        "description": "Optional category filter"
                    },
                    "isBundle": {
                        "type": "boolean",
                        "description": "Filter for bundle vs individual offerings"
                    }
                }
            }
        )
    
    def list_geographic_locations_tool(self) -> Tool:
        return Tool(
            name="list_geographic_locations",
            description="List geographic locations and their service coverage (TMF673)",
            inputSchema={
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "Optional city filter"
                    },
                    "serviceType": {
                        "type": "string",
                        "description": "Optional service type filter"
                    }
                }
            }
        )
    
    def sync_catalog_data_tool(self) -> Tool:
        return Tool(
            name="sync_catalog_data",
            description="Synchronize and validate catalog data integrity",
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
        )
    
    def create_service_specification_tool(self) -> Tool:
        return Tool(
            name="create_service_specification",
            description="Create a new service specification (TMF633)",
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
        )
    
    def create_product_offering_tool(self) -> Tool:
        return Tool(
            name="create_product_offering",
            description="Create a new product offering (TMF620)",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "description": {"type": "string"},
                    "category": {"type": "string"},
                    "isBundle": {"type": "boolean", "default": False},
                    "productSpecificationIds": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
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
        )
    
    def link_offering_to_specification_tool(self) -> Tool:
        return Tool(
            name="link_offering_to_specification",
            description="Link a product offering to service specifications",
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
        )
    
    def add_geographic_coverage_tool(self) -> Tool:
        return Tool(
            name="add_geographic_coverage",
            description="Add geographic coverage for a service specification",
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
    
    async def ensure_session(self):
        """Ensure aiohttp session is created"""
        if self.session is None:
            self.session = aiohttp.ClientSession()
    
    async def handle_tool_call(self, name: str, arguments: Any) -> List[ToolCallResult]:
        """Handle tool calls and route to appropriate TMF API"""
        try:
            await self.ensure_session()
            
            # Existing customer-facing tools
            if name == "service_qualification":
                result = await self.handle_service_qualification(arguments)
            elif name == "customer_management":
                result = await self.handle_customer_management(arguments)
            elif name == "product_ordering":
                result = await self.handle_product_ordering(arguments)
            elif name == "service_activation":
                result = await self.handle_service_activation(arguments)
            
            # New catalog management tools
            elif name == "list_service_specifications":
                result = await self.handle_list_service_specifications(arguments)
            elif name == "list_product_offerings":
                result = await self.handle_list_product_offerings(arguments)
            elif name == "list_geographic_locations":
                result = await self.handle_list_geographic_locations(arguments)
            elif name == "sync_catalog_data":
                result = await self.handle_sync_catalog_data(arguments)
            elif name == "create_service_specification":
                result = await self.handle_create_service_specification(arguments)
            elif name == "create_product_offering":
                result = await self.handle_create_product_offering(arguments)
            elif name == "link_offering_to_specification":
                result = await self.handle_link_offering_to_specification(arguments)
            elif name == "add_geographic_coverage":
                result = await self.handle_add_geographic_coverage(arguments)
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
    
    # ===== EXISTING HANDLERS =====
    
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
    
    # ===== NEW CATALOG MANAGEMENT HANDLERS =====
    
    async def handle_list_service_specifications(self, arguments: Dict) -> Dict:
        """TMF633: Service Catalog Management - List Service Specifications"""
        url = f"{CATALOG_MANAGER_URL}/tmf633/serviceSpecification"
        params = {}
        
        if arguments.get("category"):
            params["category"] = arguments["category"]
        
        async with self.session.get(url, params=params, timeout=DEFAULT_TIMEOUT) as response:
            return await response.json()
    
    async def handle_list_product_offerings(self, arguments: Dict) -> Dict:
        """TMF620: Product Catalog Management - List Product Offerings"""
        url = f"{CATALOG_MANAGER_URL}/tmf620/productOffering"
        params = {}
        
        if arguments.get("category"):
            params["category"] = arguments["category"]
        if arguments.get("isBundle") is not None:
            params["isBundle"] = arguments["isBundle"]
        
        async with self.session.get(url, params=params, timeout=DEFAULT_TIMEOUT) as response:
            return await response.json()
    
    async def handle_list_geographic_locations(self, arguments: Dict) -> Dict:
        """TMF673: Geographic Address Management - List Locations"""
        url = f"{CATALOG_MANAGER_URL}/tmf673/geographicLocation"
        params = {}
        
        if arguments.get("city"):
            params["city"] = arguments["city"]
        if arguments.get("serviceType"):
            params["serviceType"] = arguments["serviceType"]
        
        async with self.session.get(url, params=params, timeout=DEFAULT_TIMEOUT) as response:
            return await response.json()
    
    async def handle_sync_catalog_data(self, arguments: Dict) -> Dict:
        """Custom: Synchronize and validate catalog data"""
        url = f"{CATALOG_MANAGER_URL}/admin/syncCatalog"
        
        async with self.session.post(url, json=arguments, timeout=DEFAULT_TIMEOUT) as response:
            return await response.json()
    
    async def handle_create_service_specification(self, arguments: Dict) -> Dict:
        """TMF633: Create Service Specification"""
        url = f"{CATALOG_MANAGER_URL}/tmf633/serviceSpecification"
        
        async with self.session.post(url, json=arguments, timeout=DEFAULT_TIMEOUT) as response:
            return await response.json()
    
    async def handle_create_product_offering(self, arguments: Dict) -> Dict:
        """TMF620: Create Product Offering"""
        url = f"{CATALOG_MANAGER_URL}/tmf620/productOffering"
        
        async with self.session.post(url, json=arguments, timeout=DEFAULT_TIMEOUT) as response:
            return await response.json()
    
    async def handle_link_offering_to_specification(self, arguments: Dict) -> Dict:
        """Custom: Link Product Offering to Service Specifications"""
        offering_id = arguments.get("productOfferingId")
        url = f"{CATALOG_MANAGER_URL}/admin/linkOffering/{offering_id}"
        
        async with self.session.post(url, json=arguments, timeout=DEFAULT_TIMEOUT) as response:
            return await response.json()
    
    async def handle_add_geographic_coverage(self, arguments: Dict) -> Dict:
        """Custom: Add Geographic Coverage for Service Specification"""
        spec_id = arguments.get("serviceSpecificationId")
        url = f"{CATALOG_MANAGER_URL}/admin/coverage/{spec_id}"
        
        async with self.session.post(url, json=arguments, timeout=DEFAULT_TIMEOUT) as response:
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
                logger.info("Telepath MCP Server started with catalog management capabilities")
                # Keep the server running
                await asyncio.Event().wait()
        finally:
            await self.cleanup()

if __name__ == "__main__":
    server = TelecomMCPServer()
    asyncio.run(server.run())