#!/usr/bin/env python3
"""
Stdio-based MCP Server for Claude Desktop
This server communicates via stdio, which Claude Desktop expects
"""

import asyncio
import json
import sys
import logging
from typing import Any, Dict
import aiohttp

# Configure logging to stderr so it doesn't interfere with stdio communication
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger(__name__)

MCP_SERVER_URL = "http://localhost:8090"

class StdioMCPServer:
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
    
    async def send_to_http_server(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Forward message to HTTP MCP server"""
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
            logger.error(f"Error communicating with HTTP server: {str(e)}")
            return {
                "jsonrpc": "2.0",
                "error": {
                    "code": -32603,
                    "message": f"Server communication error: {str(e)}"
                },
                "id": message.get("id")
            }
    
    async def handle_stdin(self):
        """Read JSON-RPC messages from stdin"""
        reader = asyncio.StreamReader()
        protocol = asyncio.StreamReaderProtocol(reader)
        await asyncio.get_event_loop().connect_read_pipe(lambda: protocol, sys.stdin)
        
        return reader
    
    def write_response(self, response: Dict[str, Any]):
        """Write JSON-RPC response to stdout"""
        sys.stdout.write(json.dumps(response) + '\n')
        sys.stdout.flush()
    
    async def run(self):
        """Main server loop"""
        await self.setup()
        
        try:
            reader = await self.handle_stdin()
            
            logger.info("Stdio MCP Server started, waiting for messages...")
            
            while True:
                # Read line from stdin
                line = await reader.readline()
                if not line:
                    logger.info("EOF received, shutting down")
                    break
                
                try:
                    # Parse JSON-RPC message
                    message = json.loads(line.decode('utf-8').strip())
                    logger.info(f"Received: {message}")
                    
                    # Handle special cases locally
                    method = message.get('method', '')
                    
                    # For notifications, respond immediately
                    if method.startswith('notifications/'):
                        logger.info(f"Handling notification: {method}")
                        # Don't send a response for notifications
                        continue
                    
                    # Forward to HTTP server
                    response = await self.send_to_http_server(message)
                    logger.info(f"Response: {response}")
                    
                    # Write response to stdout
                    self.write_response(response)
                    
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
                    self.write_response(error_response)
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                    error_response = {
                        "jsonrpc": "2.0",
                        "error": {
                            "code": -32603,
                            "message": str(e)
                        },
                        "id": message.get("id") if 'message' in locals() else None
                    }
                    self.write_response(error_response)
                    
        except Exception as e:
            logger.error(f"Server error: {str(e)}")
        finally:
            await self.cleanup()

async def main():
    server = StdioMCPServer()
    await server.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server interrupted")
    except Exception as e:
        logger.error(f"Server crashed: {e}")
        sys.exit(1)
