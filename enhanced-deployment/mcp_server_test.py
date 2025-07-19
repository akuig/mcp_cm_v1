#!/usr/bin/env python3
"""
Simple test script to verify MCP server can be instantiated and tools registered
"""

import asyncio
import json
import logging
from mcp_server import TelecomMCPServer

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

async def test_server_creation():
    """Test that server can be created and tools registered"""
    try:
        logger.info("Creating TelecomMCPServer instance...")
        server = TelecomMCPServer()
        
        logger.info("Server created successfully!")
        
        # Test that we can access the server object
        logger.info(f"Server name: {server.server.name}")
        
        # Try to inspect tools (this might vary based on MCP version)
        if hasattr(server.server, '_tools'):
            tools = server.server._tools
            logger.info(f"Found {len(tools)} registered tools:")
            for tool_name in tools:
                logger.info(f"  - {tool_name}")
        else:
            logger.warning("Cannot inspect tools - may be using different MCP version")
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to create server: {e}", exc_info=True)
        return False

async def test_tool_schema():
    """Test that tool schemas are valid"""
    try:
        server = TelecomMCPServer()
        
        # Test each tool creation
        tools = [
            server.service_qualification_tool(),
            server.customer_management_tool(),
            server.product_ordering_tool(),
            server.service_activation_tool()
        ]
        
        for tool in tools:
            logger.info(f"Tool '{tool.name}' schema validation:")
            logger.info(f"  Description: {tool.description}")
            logger.info(f"  Schema keys: {list(tool.inputSchema.keys())}")
            
        return True
        
    except Exception as e:
        logger.error(f"Tool schema validation failed: {e}", exc_info=True)
        return False

async def main():
    """Run all tests"""
    logger.info("Starting MCP Server Tests")
    
    # Test 1: Server creation
    if await test_server_creation():
        logger.info("✅ Server creation test passed")
    else:
        logger.error("❌ Server creation test failed")
        return
    
    # Test 2: Tool schemas
    if await test_tool_schema():
        logger.info("✅ Tool schema test passed")
    else:
        logger.error("❌ Tool schema test failed")
        return
    
    logger.info("All tests passed! Server should be working correctly.")

if __name__ == "__main__":
    asyncio.run(main())
