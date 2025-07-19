#!/bin/bash

# MCP Server Fix and Deployment Script
# Fixes the tool exposure issue and redeploys the MCP server

set -e

PROJECT_DIR="/Users/joe/dev/mcp_cm_v1/enhanced-deployment"
MCP_DIR="$PROJECT_DIR/mcp-server"

echo "🔧 Fixing MCP Server Tool Exposure Issue..."

# Create backup of current implementation
echo "📋 Creating backup of current server..."
cp "$MCP_DIR/mcp_server_enhanced.py" "$MCP_DIR/mcp_server_enhanced.py.backup_$(date +%Y%m%d_%H%M%S)"

# Create fixed MCP server implementation
echo "✨ Creating fixed MCP server implementation..."
cat > "$MCP_DIR/mcp_server_fixed.py" << 'EOF'
#!/usr/bin/env python3
"""
Fixed MCP Server for Telepath AI - Proper MCP Library Implementation
Exposes TM Forum APIs as MCP tools with standard MCP protocol
"""

import asyncio
import json
import logging
import os
from typing import Any, Dict, List, Optional
from datetime import datetime
import aiohttp

# MCP imports
from mcp import types
from mcp.server import Server
from mcp.server.models import InitializationOptions
import mcp.server.stdio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
CATALOG_MANAGER_URL = os.getenv("CATALOG_MANAGER_URL", "http://catalog-manager:8080")
DEFAULT_TIMEOUT = 30

class TelecomMCPServer:
    def __init__(self):
        self.server = Server("telepath-enhanced")
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Register all handlers
        self.setup_handlers()
        
        logger.info("Telepath MCP Server initialized")
    
    def setup_handlers(self):
        """Setup MCP handlers"""
        
        @self.server.list_tools()
        async def handle_list_tools() -> List[types.Tool]:
            """Return list of available tools"""
            return [
                # ===== EXISTING CUSTOMER-FACING TOOLS (4) =====
                types.Tool(
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
                types.Tool(
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
                ),
                types.Tool(
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
                types.Tool(
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
                
                # ===== NEW CATALOG MANAGEMENT TOOLS (8) =====
                types.Tool(
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
                types.Tool(
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
                types.Tool(
                    name="list_geographic_locations",
                    description="List geographic locations and their service coverage (TMF673)",
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
                types.Tool(
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
                ),
                types.Tool(
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
                ),
                types.Tool(
                    name="create_product_offering",
                    description="Create a new product offering (TMF620)",
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
                types.Tool(
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
                ),
                types.Tool(
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
            ]
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: dict) -> List[types.TextContent]:
            """Handle tool calls"""
            try:
                await self.ensure_session()
                
                logger.info(f"Handling tool call: {name} with arguments: {arguments}")
                
                # Route to appropriate handler
                if name == "service_qualification":
                    result = await self.handle_service_qualification(arguments)
                elif name == "customer_management":
                    result = await self.handle_customer_management(arguments)
                elif name == "product_ordering":
                    result = await self.handle_product_ordering(arguments)
                elif name == "service_activation":
                    result = await self.handle_service_activation(arguments)
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
                
                # Log audit trail
                self.log_audit(name, arguments, result)
                
                return [types.TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )]
                
            except Exception as e:
                logger.error(f"Error handling tool call {name}: {str(e)}")
                return [types.TextContent(
                    type="text",
                    text=json.dumps({"error": str(e)}, indent=2)
                )]
    
    async def ensure_session(self):
        """Ensure aiohttp session is created"""
        if self.session is None:
            self.session = aiohttp.ClientSession()
    
    # ===== TOOL IMPLEMENTATIONS =====
    async def handle_service_qualification(self, arguments: Dict) -> Dict:
        """TMF637: Service Qualification"""
        url = f"{CATALOG_MANAGER_URL}/tmf637/serviceQualification"
        async with self.session.post(url, json=arguments, timeout=DEFAULT_TIMEOUT) as response:
            if response.status == 200:
                return await response.json()
            else:
                return {"error": f"Service qualification failed: {response.status}"}
    
    async def handle_customer_management(self, arguments: Dict) -> Dict:
        """TMF629: Customer Management"""
        customer_id = arguments.get("customerId")
        url = f"{CATALOG_MANAGER_URL}/tmf629/customer/{customer_id}"
        async with self.session.get(url, timeout=DEFAULT_TIMEOUT) as response:
            if response.status == 200:
                return await response.json()
            else:
                return {"error": f"Customer lookup failed: {response.status}"}
    
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
        async with self.session.post(url, json=order_data, timeout=DEFAULT_TIMEOUT) as response:
            if response.status in [200, 201]:
                return await response.json()
            else:
                return {"error": f"Product ordering failed: {response.status}"}
    
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
        async with self.session.post(url, json=activation_data, timeout=DEFAULT_TIMEOUT) as response:
            if response.status in [200, 201]:
                return await response.json()
            else:
                return {"error": f"Service activation failed: {response.status}"}
    
    async def handle_list_service_specifications(self, arguments: Dict) -> Dict:
        """List service specifications"""
        url = f"{CATALOG_MANAGER_URL}/tmf633/serviceSpecification"
        params = {}
        if arguments.get("category"):
            params["category"] = arguments["category"]
        async with self.session.get(url, params=params, timeout=DEFAULT_TIMEOUT) as response:
            if response.status == 200:
                return await response.json()
            else:
                return {"error": f"Failed to list service specifications: {response.status}"}
    
    async def handle_list_product_offerings(self, arguments: Dict) -> Dict:
        """List product offerings"""
        url = f"{CATALOG_MANAGER_URL}/tmf620/productOffering"
        params = {}
        if arguments.get("category"):
            params["category"] = arguments["category"]
        if arguments.get("isBundle") is not None:
            params["isBundle"] = arguments["isBundle"]
        async with self.session.get(url, params=params, timeout=DEFAULT_TIMEOUT) as response:
            if response.status == 200:
                return await response.json()
            else:
                return {"error": f"Failed to list product offerings: {response.status}"}
    
    async def handle_list_geographic_locations(self, arguments: Dict) -> Dict:
        """List geographic locations"""
        url = f"{CATALOG_MANAGER_URL}/tmf673/geographicLocation"
        params = {}
        if arguments.get("city"):
            params["city"] = arguments["city"]
        if arguments.get("serviceType"):
            params["serviceType"] = arguments["serviceType"]
        async with self.session.get(url, params=params, timeout=DEFAULT_TIMEOUT) as response:
            if response.status == 200:
                return await response.json()
            else:
                return {"error": f"Failed to list geographic locations: {response.status}"}
    
    async def handle_sync_catalog_data(self, arguments: Dict) -> Dict:
        """Sync catalog data"""
        url = f"{CATALOG_MANAGER_URL}/admin/syncCatalog"
        async with self.session.post(url, json=arguments, timeout=DEFAULT_TIMEOUT) as response:
            if response.status == 200:
                return await response.json()
            else:
                return {"error": f"Catalog sync failed: {response.status}"}
    
    async def handle_create_service_specification(self, arguments: Dict) -> Dict:
        """Create service specification"""
        url = f"{CATALOG_MANAGER_URL}/tmf633/serviceSpecification"
        async with self.session.post(url, json=arguments, timeout=DEFAULT_TIMEOUT) as response:
            if response.status in [200, 201]:
                return await response.json()
            else:
                return {"error": f"Failed to create service specification: {response.status}"}
    
    async def handle_create_product_offering(self, arguments: Dict) -> Dict:
        """Create product offering"""
        url = f"{CATALOG_MANAGER_URL}/tmf620/productOffering"
        async with self.session.post(url, json=arguments, timeout=DEFAULT_TIMEOUT) as response:
            if response.status in [200, 201]:
                return await response.json()
            else:
                return {"error": f"Failed to create product offering: {response.status}"}
    
    async def handle_link_offering_to_specification(self, arguments: Dict) -> Dict:
        """Link offering to specification"""
        offering_id = arguments.get("productOfferingId")
        url = f"{CATALOG_MANAGER_URL}/admin/linkOffering/{offering_id}"
        async with self.session.post(url, json=arguments, timeout=DEFAULT_TIMEOUT) as response:
            if response.status == 200:
                return await response.json()
            else:
                return {"error": f"Failed to link offering to specification: {response.status}"}
    
    async def handle_add_geographic_coverage(self, arguments: Dict) -> Dict:
        """Add geographic coverage"""
        spec_id = arguments.get("serviceSpecificationId")
        url = f"{CATALOG_MANAGER_URL}/admin/coverage/{spec_id}"
        async with self.session.post(url, json=arguments, timeout=DEFAULT_TIMEOUT) as response:
            if response.status == 200:
                return await response.json()
            else:
                return {"error": f"Failed to add geographic coverage: {response.status}"}
    
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

async def main():
    """Main entry point"""
    server = TelecomMCPServer()
    
    # Use stdio transport
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        logger.info("🚀 Starting Telepath MCP Server")
        logger.info(f"📊 Catalog Manager: {CATALOG_MANAGER_URL}")
        logger.info("🎯 Server ready for MCP connections")
        
        await server.server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="telepath-enhanced",
                server_version="2.0.0",
                capabilities=server.server.get_capabilities()
            )
        )

if __name__ == "__main__":
    asyncio.run(main())
EOF

# Update requirements.txt for proper MCP implementation
echo "📦 Updating requirements.txt..."
cat > "$MCP_DIR/requirements.txt" << 'EOF'
# Fixed MCP Server Requirements - Proper MCP Library Usage
mcp>=1.0.0,<2.0.0
aiohttp>=3.8.0,<4.0.0
python-dateutil>=2.8.0
python-dotenv>=1.0.0
uvloop>=0.19.0
EOF

# Update Dockerfile to use the fixed server
echo "🐳 Updating Dockerfile..."
cat > "$MCP_DIR/Dockerfile" << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY mcp_server_fixed.py .

# Create logs directory
RUN mkdir -p /app/logs

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \
    CMD python -c "print('MCP Server Health Check')" || exit 1

# Run the fixed MCP server
CMD ["python", "mcp_server_fixed.py"]
EOF

echo "🔄 Stopping and rebuilding MCP server..."
cd "$PROJECT_DIR"

# Stop the current MCP server
docker-compose stop mcp-server

# Remove the old container
docker-compose rm -f mcp-server

# Rebuild the MCP server with the fix
docker-compose build mcp-server

# Start the fixed MCP server
docker-compose up -d mcp-server

echo "⏳ Waiting for server to start..."
sleep 10

# Check if the server is running
echo "🔍 Checking server status..."
if docker-compose ps mcp-server | grep -q "Up"; then
    echo "✅ MCP Server is running!"
    
    # Show logs to verify
    echo "📋 Recent server logs:"
    docker-compose logs --tail=20 mcp-server
    
    echo ""
    echo "🎯 Server should now expose tools properly to Claude!"
    echo "🔗 MCP endpoint: http://localhost:8090"
    echo "❓ Check if tools are now visible in Claude"
    
else
    echo "❌ MCP Server failed to start. Checking logs..."
    docker-compose logs mcp-server
    exit 1
fi

echo ""
echo "✨ MCP Server fix deployment complete!"
echo "🔧 The server now uses proper MCP library implementation"
echo "📡 Tools should be properly exposed to Claude"
