#!/usr/bin/env python3
"""
Test FastMCP server to verify all 8 tools are available
"""

import httpx
import json
import asyncio

async def test_fastmcp_tools():
    """Test the FastMCP server with streamable HTTP"""
    base_url = "http://localhost:8090"
    
    print("🧪 Testing FastMCP Server - All 8 Tools")
    print("=" * 50)
    
    async with httpx.AsyncClient() as client:
        # Initialize session
        print("\n1. Creating session...")
        try:
            # POST to create session
            response = await client.post(f"{base_url}/mcp/stream")
            if response.status_code == 200:
                print("   ✅ Session created")
                session_data = response.headers.get("X-Session-ID", "")
                print(f"   Session ID: {session_data[:20]}...")
            else:
                print(f"   Status: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return
        
        # Test tool listing via POST
        print("\n2. Listing tools...")
        try:
            # Send a ListToolsRequest
            list_tools_request = {
                "jsonrpc": "2.0",
                "method": "tools/list",
                "params": {},
                "id": 1
            }
            
            # POST the request
            response = await client.post(
                f"{base_url}/mcp/stream",
                json=list_tools_request,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                # Get the streaming response
                get_response = await client.get(f"{base_url}/mcp/stream")
                if get_response.status_code == 200:
                    # Parse the response
                    lines = get_response.text.strip().split('\n')
                    for line in lines:
                        if line.startswith('data: '):
                            data = json.loads(line[6:])
                            if 'result' in data and 'tools' in data['result']:
                                tools = data['result']['tools']
                                print(f"   ✅ Found {len(tools)} tools:")
                                for tool in tools:
                                    print(f"      • {tool['name']}")
                                
                                # Check if all 8 are present
                                expected_tools = [
                                    "service_qualification",
                                    "customer_management",
                                    "product_ordering",
                                    "service_activation",
                                    "check_service_status",
                                    "create_trouble_ticket",
                                    "execute_remedial_action",
                                    "get_service_problems"
                                ]
                                
                                tool_names = [t['name'] for t in tools]
                                missing = [t for t in expected_tools if t not in tool_names]
                                
                                if missing:
                                    print(f"\n   ❌ Missing tools: {missing}")
                                else:
                                    print(f"\n   ✅ All 8 tools are available!")
                                break
            else:
                print(f"   ❌ Failed to list tools: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")

async def main():
    await test_fastmcp_tools()

if __name__ == "__main__":
    asyncio.run(main())
