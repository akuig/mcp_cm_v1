#!/usr/bin/env python3
"""
EXACT MATCH MCP Server - Copy exact format from working original
"""

import asyncio
import json
import logging
import os
from typing import Any, Dict, List, Optional
from datetime import datetime
import aiohttp
from mcp.server import Server
from mcp.types import Tool, TextContent, ToolResult, ToolCallResult

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
CATALOG_MANAGER_URL = os.getenv("CATALOG_MANAGER_URL", "http://catalog-manager:8080")
DEFAULT_TIMEOUT = 30

class TelecomMCPServer:
    def __init__(self):
        self.server = Server("telepath-exact-match")
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Register tools - USE EXACT SAME FORMAT AS ORIGINAL
        self.server.add_tool(self.service_qualification_tool())
        
        # Register handlers - USE EXACT SAME FORMAT AS ORIGINAL
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
    
    async def ensure_session(self):
        """Ensure aiohttp session is created"""
        if self.session is None:
            self.session = aiohttp.ClientSession()
    
    async def handle_tool_call(self, name: str, arguments: Any) -> List[ToolCallResult]:
        """Handle tool calls and route to appropriate TMF API - EXACT SAME FORMAT"""
        try:
            await self.ensure_session()
            
            logger.info(f"🔧 🎉 CLAUDE CALLED A TOOL: {name} 🎉")
            
            if name == "service_qualification":
                result = await self.handle_service_qualification(arguments)
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
        """TMF637: Service Qualification - EXACT SAME AS ORIGINAL"""
        url = f"{CATALOG_MANAGER_URL}/tmf637/serviceQualification"
        
        try:
            async with self.session.post(url, json=arguments, timeout=DEFAULT_TIMEOUT) as response:
                return await response.json()
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
        logger.info(f"Audit: {json.dumps(audit_entry)}")
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.session:
            await self.session.close()
    
    async def run(self):
        """Run the MCP server - EXACT SAME AS ORIGINAL"""
        try:
            async with self.server:
                logger.info("🚀 Telepath MCP Server started - EXACT MATCH VERSION")
                logger.info("🎯 Using ORIGINAL MCP Python library format")
                logger.info("🔧 Available tools: service_qualification")
                # Keep the server running
                await asyncio.Event().wait()
        finally:
            await self.cleanup()

if __name__ == "__main__":
    server = TelecomMCPServer()
    asyncio.run(server.run())
