#!/usr/bin/env python3
"""
MCP Server for Telepath AI - Exposes TM Forum APIs as MCP tools
FIXED VERSION - Addresses TMF622 list handling and enhanced catalog features
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional, Union
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
        
        # Register core TMF tools
        self.server.add_tool(self.service_qualification_tool())
        self.server.add_tool(self.customer_management_tool())
        self.server.add_tool(self.product_ordering_tool())
        self.server.add_tool(self.service_activation_tool())
        
        # Register enhanced catalog tools
        self.server.add_tool(self.order_management_tool())
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
    
    # ENHANCED CATALOG TOOLS
    def order_management_tool(self) -> Tool:
        """FIXED: Returns list format as per TMF622 standard"""
        return Tool(
            name="order_management",
            description="List and retrieve product orders using TMF622 standard (supports filtering by customer)",
            inputSchema={
                "type": "object",
                "properties": {
                    "orderId": {
                        "type": ["string", "null"],
                        "description": "Optional: Get specific order by ID"
                    },
                    "customerId": {
                        "type": ["string", "null"],
                        "description": "Optional: Filter orders by customer ID"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of orders to retrieve",
                        "default": 10
                    },
                    "offset": {
                        "type": "integer", 
                        "description": "Number of orders to skip for pagination",
                        "default": 0
                    }
                }
            }
        )
    
    def list_service_specifications_tool(self) -> Tool:
        return Tool(
            name="list_service_specifications",
            description="List/filter all service specifications",
            inputSchema={
                "type": "object",
                "properties": {
                    "service_type": {
                        "type": ["string", "null"],
                        "description": "Filter by service type (e.g., 'fiber_internet', 'tv', 'mobile')"
                    },
                    "search": {
                        "type": ["string", "null"],
                        "description": "Search in name and description"
                    },
                    "limit": {
                        "type": "integer",
                        "default": 100,
                        "description": "Maximum number of results"
                    },
                    "offset": {
                        "type": "integer",
                        "default": 0,
                        "description": "Number of results to skip"
                    }
                }
            }
        )
    
    def list_product_offerings_tool(self) -> Tool:
        return Tool(
            name="list_product_offerings",
            description="List/filter all product offerings",
            inputSchema={
                "type": "object",
                "properties": {
                    "category": {
                        "type": ["string", "null"],
                        "description": "Filter by category (e.g., 'internet', 'tv', 'mobile', 'bundle')"
                    },
                    "is_active": {
                        "type": ["boolean", "null"],
                        "description": "Filter by active status"
                    },
                    "min_price": {
                        "type": ["number", "null"],
                        "description": "Minimum monthly price filter"
                    },
                    "max_price": {
                        "type": ["number", "null"],
                        "description": "Maximum monthly price filter"
                    },
                    "search": {
                        "type": ["string", "null"],
                        "description": "Search in name and description"
                    },
                    "include_services": {
                        "type": "boolean",
                        "default": True,
                        "description": "Include linked service specifications in results"
                    },
                    "limit": {
                        "type": "integer",
                        "default": 100,
                        "description": "Maximum number of results"
                    },
                    "offset": {
                        "type": "integer",
                        "default": 0,
                        "description": "Number of results to skip"
                    }
                }
            }
        )
    
    def list_geographic_locations_tool(self) -> Tool:
        return Tool(
            name="list_geographic_locations",
            description="List locations with coverage info",
            inputSchema={
                "type": "object",
                "properties": {
                    "city": {
                        "type": ["string", "null"],
                        "description": "Filter by city"
                    },
                    "state_province": {
                        "type": ["string", "null"],
                        "description": "Filter by state/province"
                    },
                    "has_coverage": {
                        "type": ["boolean", "null"],
                        "description": "Filter locations with/without coverage"
                    },
                    "service_type": {
                        "type": ["string", "null"],
                        "description": "Filter by specific service type coverage"
                    },
                    "include_coverage": {
                        "type": "boolean",
                        "default": True,
                        "description": "Include detailed coverage information"
                    },
                    "limit": {
                        "type": "integer",
                        "default": 100,
                        "description": "Maximum number of results"
                    },
                    "offset": {
                        "type": "integer",
                        "default": 0,
                        "description": "Number of results to skip"
                    }
                }
            }
        )
    
    def sync_catalog_data_tool(self) -> Tool:
        return Tool(
            name="sync_catalog_data",
            description="Validate and sync catalog integrity",
            inputSchema={
                "type": "object",
                "properties": {
                    "sync_type": {
                        "type": "string",
                        "default": "full",
                        "description": "Type of sync to perform ('full', 'integrity_check', 'coverage_sync')"
                    }
                }
            }
        )
    
    def create_service_specification_tool(self) -> Tool:
        return Tool(
            name="create_service_specification",
            description="Create new service specification",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Service specification name"
                    },
                    "service_type": {
                        "type": "string",
                        "description": "Type of service (e.g., 'fiber_internet', 'tv', 'mobile')"
                    },
                    "description": {
                        "type": "string",
                        "description": "Detailed description of the service"
                    },
                    "id": {
                        "type": ["string", "null"],
                        "description": "Optional custom ID (auto-generated if not provided)"
                    }
                },
                "required": ["name", "service_type", "description"]
            }
        )
    
    def create_product_offering_tool(self) -> Tool:
        return Tool(
            name="create_product_offering",
            description="Create new product offering",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Product offering name"
                    },
                    "description": {
                        "type": "string",
                        "description": "Detailed description"
                    },
                    "category": {
                        "type": "string",
                        "description": "Product category (e.g., 'internet', 'tv', 'mobile', 'bundle')"
                    },
                    "price_monthly": {
                        "type": "number",
                        "description": "Monthly price in dollars"
                    },
                    "price_setup": {
                        "type": "number",
                        "default": 0.0,
                        "description": "One-time setup fee"
                    },
                    "contract_length_months": {
                        "type": "integer",
                        "default": 0,
                        "description": "Contract length in months (default 0 for no contract)"
                    },
                    "is_active": {
                        "type": "boolean",
                        "default": True,
                        "description": "Whether the offering is active"
                    },
                    "id": {
                        "type": ["string", "null"],
                        "description": "Optional custom ID (auto-generated if not provided)"
                    }
                },
                "required": ["name", "description", "category", "price_monthly"]
            }
        )
    
    def link_offering_to_specification_tool(self) -> Tool:
        return Tool(
            name="link_offering_to_specification",
            description="Link product offering to service specification",
            inputSchema={
                "type": "object",
                "properties": {
                    "product_offering_id": {
                        "type": "string",
                        "description": "ID of the product offering"
                    },
                    "service_specification_id": {
                        "type": "string",
                        "description": "ID of the service specification to link"
                    },
                    "is_primary": {
                        "type": "boolean",
                        "default": False,
                        "description": "Whether this is the primary service for the offering"
                    }
                },
                "required": ["product_offering_id", "service_specification_id"]
            }
        )
    
    def add_geographic_coverage_tool(self) -> Tool:
        return Tool(
            name="add_geographic_coverage",
            description="Add coverage area for services",
            inputSchema={
                "type": "object",
                "properties": {
                    "location_id": {
                        "type": "string",
                        "description": "Geographic location ID"
                    },
                    "service_type": {
                        "type": "string",
                        "description": "Type of service coverage to add"
                    },
                    "available": {
                        "type": "boolean",
                        "default": True,
                        "description": "Whether service is available"
                    },
                    "max_speed_mbps": {
                        "type": ["integer", "null"],
                        "description": "Maximum speed in Mbps for internet services"
                    },
                    "coverage_quality": {
                        "type": "string",
                        "default": "good",
                        "description": "Coverage quality ('excellent', 'good', 'fair', 'poor')"
                    },
                    "technology": {
                        "type": ["string", "null"],
                        "description": "Technology used ('fiber', 'cable', 'dsl', 'wireless', '5G', etc.)"
                    },
                    "signal_strength": {
                        "type": ["integer", "null"],
                        "description": "Signal strength (1-5 scale for wireless services)"
                    }
                },
                "required": ["location_id", "service_type"]
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
            
            # Core TMF API calls
            if name == "service_qualification":
                result = await self.handle_service_qualification(arguments)
            elif name == "customer_management":
                result = await self.handle_customer_management(arguments)
            elif name == "product_ordering":
                result = await self.handle_product_ordering(arguments)
            elif name == "service_activation":
                result = await self.handle_service_activation(arguments)
            
            # Enhanced catalog API calls
            elif name == "order_management":
                result = await self.handle_order_management(arguments)
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
    
    # CORE TMF API HANDLERS
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
        """TMF622: Product Ordering (CREATE)"""
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
    
    # ENHANCED CATALOG API HANDLERS
    async def handle_order_management(self, arguments: Dict) -> Union[List, Dict]:
        """TMF622: Order Management (GET) - FIXED to handle list responses"""
        params = {}
        if arguments.get("customerId"):
            params["customerId"] = arguments["customerId"]
        if arguments.get("limit"):
            params["limit"] = arguments["limit"]
        if arguments.get("offset"):
            params["offset"] = arguments["offset"]
        
        if arguments.get("orderId"):
            # Get specific order
            url = f"{CATALOG_MANAGER_URL}/tmf622/productOrder/{arguments['orderId']}"
            async with self.session.get(url, timeout=DEFAULT_TIMEOUT) as response:
                return await response.json()
        else:
            # Get list of orders - TMF622 standard returns array
            url = f"{CATALOG_MANAGER_URL}/tmf622/productOrder"
            async with self.session.get(url, params=params, timeout=DEFAULT_TIMEOUT) as response:
                return await response.json()  # This will be a list
    
    async def handle_list_service_specifications(self, arguments: Dict) -> Dict:
        """Enhanced Catalog: List Service Specifications"""
        params = {k: v for k, v in arguments.items() if v is not None}
        url = f"{CATALOG_MANAGER_URL}/api/service-specifications"
        
        async with self.session.get(url, params=params, timeout=DEFAULT_TIMEOUT) as response:
            return await response.json()
    
    async def handle_list_product_offerings(self, arguments: Dict) -> Dict:
        """Enhanced Catalog: List Product Offerings"""
        params = {k: v for k, v in arguments.items() if v is not None}
        url = f"{CATALOG_MANAGER_URL}/api/product-offerings"
        
        async with self.session.get(url, params=params, timeout=DEFAULT_TIMEOUT) as response:
            return await response.json()
    
    async def handle_list_geographic_locations(self, arguments: Dict) -> Dict:
        """Enhanced Catalog: List Geographic Locations"""
        params = {k: v for k, v in arguments.items() if v is not None}
        url = f"{CATALOG_MANAGER_URL}/api/geographic-locations"
        
        async with self.session.get(url, params=params, timeout=DEFAULT_TIMEOUT) as response:
            return await response.json()
    
    async def handle_sync_catalog_data(self, arguments: Dict) -> Dict:
        """Enhanced Catalog: Sync Catalog Data"""
        sync_type = arguments.get("sync_type", "full")
        url = f"{CATALOG_MANAGER_URL}/api/sync-catalog-data"
        
        async with self.session.post(url, json={"sync_type": sync_type}, timeout=DEFAULT_TIMEOUT) as response:
            return await response.json()
    
    async def handle_create_service_specification(self, arguments: Dict) -> Dict:
        """Enhanced Catalog: Create Service Specification"""
        url = f"{CATALOG_MANAGER_URL}/api/create-service-specification"
        
        async with self.session.post(url, json=arguments, timeout=DEFAULT_TIMEOUT) as response:
            return await response.json()
    
    async def handle_create_product_offering(self, arguments: Dict) -> Dict:
        """Enhanced Catalog: Create Product Offering"""
        url = f"{CATALOG_MANAGER_URL}/api/create-product-offering"
        
        async with self.session.post(url, json=arguments, timeout=DEFAULT_TIMEOUT) as response:
            return await response.json()
    
    async def handle_link_offering_to_specification(self, arguments: Dict) -> Dict:
        """Enhanced Catalog: Link Offering to Specification"""
        url = f"{CATALOG_MANAGER_URL}/api/link-offering-to-specification"
        
        async with self.session.post(url, json=arguments, timeout=DEFAULT_TIMEOUT) as response:
            return await response.json()
    
    async def handle_add_geographic_coverage(self, arguments: Dict) -> Dict:
        """Enhanced Catalog: Add Geographic Coverage"""
        url = f"{CATALOG_MANAGER_URL}/api/add-geographic-coverage"
        
        async with self.session.post(url, json=arguments, timeout=DEFAULT_TIMEOUT) as response:
            return await response.json()
    
    def log_audit(self, action: str, request: Dict, response: Union[Dict, List]):
        """Log audit trail for compliance"""
        audit_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "correlationId": f"{action}-{datetime.utcnow().timestamp()}",
            "action": action,
            "requestPayload": request,
            "responsePayload": response,
            "status": "Success" if (isinstance(response, dict) and "error" not in response) or isinstance(response, list) else "Failed"
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
                logger.info("Telepath MCP Server started with enhanced catalog support")
                # Keep the server running
                await asyncio.Event().wait()
        finally:
            await self.cleanup()

if __name__ == "__main__":
    server = TelecomMCPServer()
    asyncio.run(server.run())
