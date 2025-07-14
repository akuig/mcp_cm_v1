#!/usr/bin/env python3
"""
Test the working MCP HTTP server
"""

import httpx
import json
import asyncio

async def test_mcp_endpoints():
    """Test all MCP endpoints"""
    base_url = "http://localhost:8090"
    
    print("🧪 Testing MCP Working HTTP Server")
    print("=" * 50)
    
    async with httpx.AsyncClient() as client:
        # Test 1: Health check
        print("\n1. Health Check")
        try:
            response = await client.get(f"{base_url}/health")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.json()}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Test 2: MCP info
        print("\n2. MCP Info")
        try:
            response = await client.get(f"{base_url}/mcp")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.json()}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Test 3: Initialize
        print("\n3. Initialize Request")
        try:
            init_request = {
                "jsonrpc": "2.0",
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {}
                },
                "id": 1
            }
            response = await client.post(f"{base_url}/mcp/stream", json=init_request)
            print(f"   Status: {response.status_code}")
            result = response.json()
            print(f"   Protocol: {result.get('result', {}).get('protocolVersion')}")
            print(f"   Server: {result.get('result', {}).get('serverInfo', {}).get('name')}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Test 4: List tools
        print("\n4. List Tools")
        try:
            list_request = {
                "jsonrpc": "2.0",
                "method": "tools/list",
                "params": {},
                "id": 2
            }
            response = await client.post(f"{base_url}/mcp/stream", json=list_request)
            print(f"   Status: {response.status_code}")
            result = response.json()
            tools = result.get('result', {}).get('tools', [])
            print(f"   Found {len(tools)} tools:")
            for tool in tools[:3]:  # Show first 3
                print(f"   - {tool['name']}: {tool['description'][:50]}...")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Test 5: Call a tool
        print("\n5. Test Tool Call (check_service_status)")
        try:
            call_request = {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": "check_service_status",
                    "arguments": {
                        "location": {
                            "streetName": "Main Street",
                            "city": "Dublin"
                        }
                    }
                },
                "id": 3
            }
            response = await client.post(f"{base_url}/mcp/stream", json=call_request)
            print(f"   Status: {response.status_code}")
            result = response.json()
            if 'result' in result:
                content = result['result'].get('content', [{}])[0].get('text', '{}')
                data = json.loads(content)
                print(f"   Service Status: {data.get('status', 'unknown')}")
                if data.get('networkFaults'):
                    print(f"   Fault Detected: {data['networkFaults'][0]['description']}")
            else:
                print(f"   Error: {result.get('error', {}).get('message', 'Unknown error')}")
        except Exception as e:
            print(f"   ❌ Error: {e}")

async def main():
    await test_mcp_endpoints()
    print("\n" + "=" * 50)
    print("✅ Testing complete!")

if __name__ == "__main__":
    asyncio.run(main())
