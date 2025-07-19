#!/usr/bin/env python3
"""
Test script to verify MCP server tools are working correctly
"""

import asyncio
import aiohttp
import json
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MCP_SERVER_URL = "http://localhost:8090"

async def test_mcp_server():
    """Test MCP server functionality"""
    async with aiohttp.ClientSession() as session:
        
        # Test 1: Health check
        logger.info("🔍 Testing health endpoint...")
        try:
            async with session.get(f"{MCP_SERVER_URL}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"✅ Health check passed: {data}")
                else:
                    logger.error(f"❌ Health check failed: {response.status}")
                    return False
        except Exception as e:
            logger.error(f"❌ Health check error: {e}")
            return False
        
        # Test 2: MCP info endpoint
        logger.info("🔍 Testing MCP info endpoint...")
        try:
            async with session.get(f"{MCP_SERVER_URL}/mcp") as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"✅ MCP info: {data}")
                else:
                    logger.error(f"❌ MCP info failed: {response.status}")
                    return False
        except Exception as e:
            logger.error(f"❌ MCP info error: {e}")
            return False
        
        # Test 3: Tools list via JSON-RPC
        logger.info("🔍 Testing tools list via JSON-RPC...")
        try:
            request_data = {
                "jsonrpc": "2.0",
                "id": "test-1",
                "method": "tools/list",
                "params": {}
            }
            
            async with session.post(
                f"{MCP_SERVER_URL}/mcp/stream",
                json=request_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    if "result" in data and "tools" in data["result"]:
                        tools = data["result"]["tools"]
                        logger.info(f"✅ Found {len(tools)} tools:")
                        for tool in tools:
                            logger.info(f"   - {tool['name']}: {tool['description']}")
                    else:
                        logger.error(f"❌ Invalid tools response: {data}")
                        return False
                else:
                    logger.error(f"❌ Tools list failed: {response.status}")
                    return False
        except Exception as e:
            logger.error(f"❌ Tools list error: {e}")
            return False
        
        # Test 4: Initialize MCP connection
        logger.info("🔍 Testing MCP initialization...")
        try:
            request_data = {
                "jsonrpc": "2.0",
                "id": "test-2",
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {}
                    },
                    "clientInfo": {
                        "name": "test-client",
                        "version": "1.0.0"
                    }
                }
            }
            
            async with session.post(
                f"{MCP_SERVER_URL}/mcp/stream",
                json=request_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    if "result" in data:
                        logger.info(f"✅ MCP initialization successful: {data['result'].get('serverInfo', {}).get('name')}")
                    else:
                        logger.error(f"❌ Invalid initialization response: {data}")
                        return False
                else:
                    logger.error(f"❌ MCP initialization failed: {response.status}")
                    return False
        except Exception as e:
            logger.error(f"❌ MCP initialization error: {e}")
            return False
        
        # Test 5: Test a simple tool call
        logger.info("🔍 Testing a simple tool call...")
        try:
            request_data = {
                "jsonrpc": "2.0",
                "id": "test-3",
                "method": "tools/call",
                "params": {
                    "name": "list_service_specifications",
                    "arguments": {}
                }
            }
            
            async with session.post(
                f"{MCP_SERVER_URL}/mcp/stream",
                json=request_data,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    if "result" in data:
                        logger.info("✅ Tool call successful!")
                        logger.info(f"   Response: {data['result']}")
                    else:
                        logger.error(f"❌ Tool call failed: {data}")
                        return False
                else:
                    logger.error(f"❌ Tool call failed: {response.status}")
                    return False
        except Exception as e:
            logger.error(f"❌ Tool call error: {e}")
            return False
        
        logger.info("🎉 All MCP server tests passed!")
        return True

async def main():
    """Main test function"""
    logger.info("🚀 Starting MCP Server Test Suite")
    
    success = await test_mcp_server()
    
    if success:
        logger.info("✅ All tests passed! MCP server is working correctly.")
        sys.exit(0)
    else:
        logger.error("❌ Some tests failed. Check the logs above.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
