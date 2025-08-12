#!/usr/bin/env python3
"""
Enhanced MCP Server for Telepath AI - Fixed version with proper error handling
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
        
        # Register catalog creation tools
        self.server.add_tool(self.create_service_specification_tool())
        self.server.add_tool(self.create_product_offering_tool())
        self.server.add_tool(self.link_offering_to_specification_tool())
        self.server.add_tool(self.add_geographic_coverage_tool())
        
        # Register handlers
        self.server.set_call_tool_handler(self.handle_tool_call)
    
    # Core TMF Tools (unchanged)
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
    
    # Enhanced Catalog Tools
    def order_management_tool(self) -> Tool:
        return Tool(
            name="order_management",
            description="List and retrieve product orders using TMF622 standard (supports filtering by customer)",
            inputSchema={
                "type": "object",
                "properties": {
                    "orderId": {"type": "string", "description": "Optional: Get specific order by ID"},
                    "customerId": {"type": "string", "description": "Optional: Filter orders by customer ID"},
                    "limit": {"type": "integer", "default": 10, "description": "Maximum number of orders to retrieve"},
                    "offset": {"type": "integer", "default": 0, "description": "Number of orders to skip for pagination"}
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
                    "service_type": {"type": "string", "description": "Filter by service type (e.g., 'fiber_internet', 'tv', 'mobile')"},
                    "search": {"type": "string", "description": "Search in name and description"},
                    "limit": {"type": "integer", "default": 100},
                    "offset": {"type": "integer", "default": 0}
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
                    "category": {"type": "string", "description": "Filter by category (e.g., 'internet', 'tv', 'mobile', 'bundle')"},
                    "is_active": {"type": "boolean", "description": "Filter by active status"},
                    "min_price": {"type": "number", "description": "Minimum monthly price filter"},
                    "max_price": {"type": "number", "description": "Maximum monthly price filter"},
                    "search": {"type": "string", "description": "Search in name and description"},
                    "include_services": {"type": "boolean", "default": True, "description": "Include linked service specifications"},
                    "limit": {"type": "integer", "default": 100},
                    "offset": {"type": "integer", "default": 0}
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
                    "city": {"type": "string", "description": "Filter by city"},
                    "state_province": {"type": "string", "description": "Filter by state/province"},
                    "has_coverage": {"type": "boolean", "description": "Filter locations with/without coverage"},
                    "service_type": {"type": "string", "description": "Filter by specific service type coverage"},
                    "include_coverage": {"type": "boolean", "default": True},
                    "limit": {"type": "integer", "default": 100},
                    "offset": {"type": "integer", "default": 0}
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
                    "name": {"type": "string"},
                    "service_type": {"type": "string", "description": "Type of service (e.g., 'fiber_internet', 'tv', 'mobile')"},
                    "description": {"type": "string"},
                    "id": {"type": "string", "description": "Optional custom ID (auto-generated if not provided)"}
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
                    "name": {"type": "string"},
                    "description": {"type": "string"},
                    "category": {"type": "string", "description": "Product category (e.g., 'internet', 'tv', 'mobile', 'bundle')"},
                    "price_monthly": {"type": "number"},
                    "price_setup": {"type": "number", "default": 0},
                    "contract_length_months": {"type": "integer", "default": 0},
                    "is_active": {"type": "boolean", "default": True},
                    "id": {"type": "string", "description": "Optional custom ID"}
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
                    "product_offering_id": {"type": "string"},
                    "service_specification_id": {"type": "string"},
                    "is_primary": {"type": "boolean", "default": False}
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
                    "location_id": {"type": "string"},
                    "service_type": {"type": "string"},
                    "available": {"type": "boolean", "default": True},
                    "max_speed_mbps": {"type": "integer", "description": "Maximum speed in Mbps for internet services"},
                    "coverage_quality": {"type": "string", "default": "good", "description": "Coverage quality ('excellent', 'good', 'fair', 'poor')"},
                    "technology": {"type": "string", "description": "Technology used ('fiber', 'cable', 'dsl', 'wireless', '5G', etc.)"},
                    "signal_strength": {"type": "integer", "description": "Signal strength (1-5 scale for wireless services)"}
                },
                "required": ["location_id", "service_type"]
            }
        )
    
    async def ensure_session(self):
        """Ensure aiohttp session is created"""
        if self.session is None:
            self.session = aiohttp.ClientSession()
    
    async def handle_tool_call(self, name: str, arguments: Any) -> List[ToolCallResult]:
        """Handle tool calls and route to appropriate API"""
        try:
            await self.ensure_session()
            
            # Route to appropriate handler
            handlers = {
                "service_qualification": self.handle_service_qualification,
                "customer_management": self.handle_customer_management,
                "product_ordering": self.handle_product_ordering,
                "service_activation": self.handle_service_activation,
                "order_management": self.handle_order_management,
                "list_service_specifications": self.handle_list_service_specifications,
                "list_product_offerings": self.handle_list_product_offerings,
                "list_geographic_locations": self.handle_list_geographic_locations,
                "sync_catalog_data": self.handle_sync_catalog_data,
                "create_service_specification": self.handle_create_service_specification,
                "create_product_offering": self.handle_create_product_offering,
                "link_offering_to_specification": self.handle_link_offering_to_specification,
                "add_geographic_coverage": self.handle_add_geographic_coverage
            }
            
            handler = handlers.get(name)
            if not handler:
                result = {"error": f"Unknown tool: {name}"}
            else:
                result = await handler(arguments)
            
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
    
    # Core TMF Handlers (unchanged)
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
    
    # Enhanced Catalog Handlers - Fixed to handle list/dict responses
    async def handle_order_management(self, arguments: Dict) -> Dict:
        """Handle order management with proper response formatting"""
        try:
            # Try multiple possible endpoints
            endpoints = [
                "/api/orders",
                "/api/product-orders",
                "/tmf622/productOrder"
            ]
            
            params = {}
            if arguments.get("customerId"):
                params["customerId"] = arguments["customerId"]
            if arguments.get("limit"):
                params["limit"] = arguments["limit"]
            if arguments.get("offset"):
                params["offset"] = arguments["offset"]
            
            for endpoint in endpoints:
                url = f"{CATALOG_MANAGER_URL}{endpoint}"
                if arguments.get("orderId"):
                    url = f"{url}/{arguments['orderId']}"
                
                try:
                    async with self.session.get(url, params=params, timeout=DEFAULT_TIMEOUT) as response:
                        if response.status == 200:
                            data = await response.json()
                            # Normalize response to always return a dict
                            if isinstance(data, list):
                                return {"orders": data, "total": len(data)}
                            return data
                except:
                    continue
            
            return {"error": "Order management endpoint not found", "tried_endpoints": endpoints}
        except Exception as e:
            return {"error": f"Order management failed: {str(e)}"}
    
    async def handle_list_service_specifications(self, arguments: Dict) -> Dict:
        """Handle service specifications listing with proper response formatting"""
        try:
            # Try multiple possible endpoints
            endpoints = [
                "/api/service-specifications",
                "/tmf633/serviceSpecification"
            ]
            
            params = {k: v for k, v in arguments.items() if v is not None}
            
            for endpoint in endpoints:
                url = f"{CATALOG_MANAGER_URL}{endpoint}"
                
                try:
                    async with self.session.get(url, params=params, timeout=DEFAULT_TIMEOUT) as response:
                        if response.status == 200:
                            data = await response.json()
                            # Normalize response to always return a dict
                            if isinstance(data, list):
                                return {"serviceSpecifications": data, "total": len(data)}
                            return data
                except:
                    continue
            
            return {"error": "Service specifications endpoint not found", "tried_endpoints": endpoints}
        except Exception as e:
            return {"error": f"List service specifications failed: {str(e)}"}
    
    async def handle_list_product_offerings(self, arguments: Dict) -> Dict:
        """Handle product offerings listing with proper response formatting"""
        try:
            # Try multiple possible endpoints
            endpoints = [
                "/api/product-offerings",
                "/tmf620/productOffering"
            ]
            
            params = {k: v for k, v in arguments.items() if v is not None}
            
            for endpoint in endpoints:
                url = f"{CATALOG_MANAGER_URL}{endpoint}"
                
                try:
                    async with self.session.get(url, params=params, timeout=DEFAULT_TIMEOUT) as response:
                        if response.status == 200:
                            data = await response.json()
                            # Normalize response to always return a dict
                            if isinstance(data, list):
                                return {"productOfferings": data, "total": len(data)}
                            return data
                        elif response.status == 404:
                            continue
                except:
                    continue
            
            return {"error": "Product offerings endpoint not found", "tried_endpoints": endpoints}
        except Exception as e:
            return {"error": f"List product offerings failed: {str(e)}"}
    
    async def handle_list_geographic_locations(self, arguments: Dict) -> Dict:
        """Handle geographic locations listing with proper response formatting"""
        try:
            # Try multiple possible endpoints
            endpoints = [
                "/api/geographic-locations",
                "/tmf673/geographicLocation"
            ]
            
            params = {k: v for k, v in arguments.items() if v is not None}
            
            for endpoint in endpoints:
                url = f"{CATALOG_MANAGER_URL}{endpoint}"
                
                try:
                    async with self.session.get(url, params=params, timeout=DEFAULT_TIMEOUT) as response:
                        if response.status == 200:
                            data = await response.json()
                            # Normalize response to always return a dict
                            if isinstance(data, list):
                                return {"geographicLocations": data, "total": len(data)}
                            return data
                        elif response.status == 404:
                            continue
                except:
                    continue
            
            return {"error": "Geographic locations endpoint not found", "tried_endpoints": endpoints}
        except Exception as e:
            return {"error": f"List geographic locations failed: {str(e)}"}
    
    async def handle_sync_catalog_data(self, arguments: Dict) -> Dict:
        """Handle catalog data sync"""
        try:
            url = f"{CATALOG_MANAGER_URL}/api/sync"
            sync_type = arguments.get("sync_type", "full")
            
            async with self.session.post(url, json={"type": sync_type}, timeout=DEFAULT_TIMEOUT) as response:
                if response.status == 200:
                    return await response.json()
                elif response.status == 404:
                    # Try alternative endpoint
                    url = f"{CATALOG_MANAGER_URL}/api/catalog/sync"
                    async with self.session.post(url, json={"type": sync_type}, timeout=DEFAULT_TIMEOUT) as alt_response:
                        if alt_response.status == 200:
                            return await alt_response.json()
                
                return {"error": f"Sync endpoint returned status {response.status}"}
        except Exception as e:
            return {"error": f"Sync catalog data failed: {str(e)}"}
    
    async def handle_create_service_specification(self, arguments: Dict) -> Dict:
        """Create service specification"""
        try:
            endpoints = [
                "/api/service-specifications",
                "/tmf633/serviceSpecification"
            ]
            
            for endpoint in endpoints:
                url = f"{CATALOG_MANAGER_URL}{endpoint}"
                
                try:
                    async with self.session.post(url, json=arguments, timeout=DEFAULT_TIMEOUT) as response:
                        if response.status in [200, 201]:
                            return await response.json()
                except:
                    continue
            
            return {"error": "Create service specification endpoint not found"}
        except Exception as e:
            return {"error": f"Create service specification failed: {str(e)}"}
    
    async def handle_create_product_offering(self, arguments: Dict) -> Dict:
        """Create product offering"""
        try:
            endpoints = [
                "/api/product-offerings",
                "/tmf620/productOffering"
            ]
            
            for endpoint in endpoints:
                url = f"{CATALOG_MANAGER_URL}{endpoint}"
                
                try:
                    async with self.session.post(url, json=arguments, timeout=DEFAULT_TIMEOUT) as response:
                        if response.status in [200, 201]:
                            return await response.json()
                except:
                    continue
            
            return {"error": "Create product offering endpoint not found"}
        except Exception as e:
            return {"error": f"Create product offering failed: {str(e)}"}
    
    async def handle_link_offering_to_specification(self, arguments: Dict) -> Dict:
        """Link product offering to service specification"""
        try:
            product_id = arguments["product_offering_id"]
            service_id = arguments["service_specification_id"]
            
            endpoints = [
                f"/api/product-offerings/{product_id}/link-service",
                f"/api/product-service-links"
            ]
            
            for endpoint in endpoints:
                url = f"{CATALOG_MANAGER_URL}{endpoint}"
                
                try:
                    async with self.session.post(url, json=arguments, timeout=DEFAULT_TIMEOUT) as response:
                        if response.status in [200, 201]:
                            return await response.json()
                except:
                    continue
            
            return {"error": "Link endpoint not found"}
        except Exception as e:
            return {"error": f"Link offering to specification failed: {str(e)}"}
    
    async def handle_add_geographic_coverage(self, arguments: Dict) -> Dict:
        """Add geographic coverage"""
        try:
            location_id = arguments["location_id"]
            
            endpoints = [
                f"/api/geographic-locations/{location_id}/coverage",
                "/api/coverage"
            ]
            
            for endpoint in endpoints:
                url = f"{CATALOG_MANAGER_URL}{endpoint}"
                
                try:
                    async with self.session.post(url, json=arguments, timeout=DEFAULT_TIMEOUT) as response:
                        if response.status in [200, 201]:
                            return await response.json()
                except:
                    continue
            
            return {"error": "Add coverage endpoint not found"}
        except Exception as e:
            return {"error": f"Add geographic coverage failed: {str(e)}"}
    
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
                logger.info("Telepath MCP Server started - Enhanced version with error handling")
                logger.info(f"Connecting to Catalog Manager at: {CATALOG_MANAGER_URL}")
                # Keep the server running
                await asyncio.Event().wait()
        finally:
            await self.cleanup()

if __name__ == "__main__":
    server = TelecomMCPServer()
    asyncio.run(server.run())
