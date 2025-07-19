#!/usr/bin/env python3
"""
MCP Server for Telepath AI - EXACT COPY of working FastMCP approach with 1 tool
"""

import os
import logging
import asyncio
import aiohttp
from typing import Dict, Any
from mcp.server.fastmcp import FastMCP

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
PORT = os.getenv("PORT", "8090")
HOST = os.getenv("HOST", "0.0.0.0")
CATALOG_MANAGER_URL = "http://catalog-manager:8080"
DEFAULT_TIMEOUT = 30

# Create the MCP server - EXACT SAME AS WORKING VERSION
mcp = FastMCP("telepath-mcp", port=PORT, host=HOST, debug=True, log_level="INFO")

# Global session for HTTP requests
session = None

async def ensure_session():
    """Ensure aiohttp session is created"""
    global session
    if session is None:
        session = aiohttp.ClientSession()

async def cleanup_session():
    """Cleanup aiohttp session"""
    global session
    if session:
        await session.close()
        session = None

def log_audit(action: str, request: Dict, response: Dict):
    """Log audit trail for compliance"""
    from datetime import datetime
    audit_entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "correlationId": f"{action}-{datetime.utcnow().timestamp()}",
        "action": action,
        "requestPayload": request,
        "responsePayload": response,
        "status": "Success" if "error" not in response else "Failed"
    }
    logger.info(f"🎉 CLAUDE USED TOOL! Audit: {audit_entry}")

@mcp.tool()
async def service_qualification(
    address: Dict[str, str],
    serviceSpecification: Dict[str, str]
) -> Dict[str, Any]:
    """Check if a service is available at a specific location (TMF637)
    
    Args:
        address: Address with streetName, streetNumber, and city
        serviceSpecification: Service specification with id and name
    
    Returns:
        Service qualification result
    """
    await ensure_session()
    
    url = f"{CATALOG_MANAGER_URL}/tmf637/serviceQualification"
    request_data = {
        "address": address,
        "serviceSpecification": serviceSpecification
    }
    
    try:
        async with session.post(url, json=request_data, timeout=DEFAULT_TIMEOUT) as response:
            result = await response.json()
            log_audit("service_qualification", request_data, result)
            return result
    except Exception as e:
        error_result = {"error": str(e)}
        log_audit("service_qualification", request_data, error_result)
        raise Exception(f"Service qualification failed: {str(e)}")

if __name__ == "__main__":
    print(f"🚀 Running Telepath MCP Server (EXACT WORKING APPROACH) on {HOST}:{PORT}")
    print(f"📊 Catalog Manager URL: {CATALOG_MANAGER_URL}")
    print(f"🔧 Available tools: service_qualification")
    try:
        mcp.run(transport="streamable-http")
    finally:
        # Cleanup session if exists
        if session:
            asyncio.run(cleanup_session())
