#!/usr/bin/env python3
"""
MCP Inspector Bridge - Adapts HTTP streaming MCP server for MCP Inspector
"""

import asyncio
import json
import sys
import aiohttp
from typing import Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

MCP_SERVER_URL = "http://localhost:8090"

class MCPBridge:
    """Bridge between stdio (for MCP Inspector) and HTTP streaming MCP server"""
    
    def __init__(self):
        self.session = None
        self.request_id = 0
    
    async def setup(self):
        """Setup HTTP session"""
        self.session = aiohttp.ClientSession()
    
    async def cleanup(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()
    
    async def send_to_server(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Send message to HTTP streaming MCP server"""
        try:
            async with self.session.post(
                f"{MCP_SERVER_URL}/mcp/stream",
                json=message,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json-stream"
                }
            ) as response:
                # Read the streaming response
                full_response = ""
                async for chunk in response.content:
                    full_response += chunk.decode('utf-8')
                
                # Parse the JSON response
                for line in full_response.strip().split('\n'):
                    if line:
                        return json.loads(line)
                
                return {"error": "No response received"}
                
        except Exception as e:
            logger.error(f"Error communicating with server: {str(e)}")
            return {
                "jsonrpc": "2.0",
                "error": {
                    "code": -32603,
                    "message": f"Server communication error: {str(e)}"
                },
                "id": message.get("id")
            }
    
    async def run(self):
        """Main bridge loop - read from stdin, forward to HTTP server, write to stdout"""
        await self.setup()
        
        try:
            reader = asyncio.StreamReader()
            protocol = asyncio.StreamReaderProtocol(reader)
            await asyncio.get_event_loop().connect_read_pipe(lambda: protocol, sys.stdin)
            
            writer = sys.stdout
            
            while True:
                # Read line from stdin
                line = await reader.readline()
                if not line:
                    break
                
                try:
                    # Parse JSON-RPC message
                    message = json.loads(line.decode('utf-8').strip())
                    logger.info(f"Received from Inspector/Claude: {message}")
                    
                    # Handle notifications (no response needed)
                    if 'id' not in message and message.get('method', '').startswith('notifications/'):
                        logger.info(f"Ignoring notification: {message.get('method')}")
                        continue
                    
                    # Forward to HTTP server
                    response = await self.send_to_server(message)
                    logger.info(f"Response from server: {response}")
                    
                    # Write response to stdout
                    writer.write(json.dumps(response) + '\n')
                    writer.flush()
                    
                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON received: {e}")
                    error_response = {
                        "jsonrpc": "2.0",
                        "error": {
                            "code": -32700,
                            "message": "Parse error"
                        },
                        "id": None
                    }
                    writer.write(json.dumps(error_response) + '\n')
                    writer.flush()
                    
        except Exception as e:
            logger.error(f"Bridge error: {str(e)}")
        finally:
            await self.cleanup()

async def main():
    bridge = MCPBridge()
    await bridge.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
