#!/usr/bin/env python3
"""
Test MCP HTTP Streaming endpoints
"""

import httpx
import json
import asyncio

async def test_mcp_http_streaming():
    """Test the MCP HTTP streaming server"""
    base_url = "http://localhost:8090"
    
    print("🧪 Testing MCP HTTP Streaming Server")
    print("=" * 50)
    
    async with httpx.AsyncClient() as client:
        # Test 1: Health check
        print("\n1. Testing health endpoint...")
        try:
            response = await client.get(f"{base_url}/health")
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Health check passed")
                print(f"   Server: {data.get('server')}")
                print(f"   Transport: {data.get('transport')}")
            else:
                print(f"   ❌ Health check failed: {response.status_code}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Test 2: Check MCP info endpoint
        print("\n2. Testing MCP info endpoint...")
        try:
            response = await client.get(f"{base_url}/mcp")
            print(f"   Response status: {response.status_code}")
            if response.status_code == 200:
                print("   ✅ MCP endpoint accessible")
        except Exception as e:
            print(f"   ℹ️  MCP endpoint: {e}")
        
        # Test 3: List tools via streaming
        print("\n3. Testing tools listing...")
        try:
            # Send initialization request
            init_request = {
                "jsonrpc": "2.0",
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {}
                },
                "id": 1
            }
            
            response = await client.post(
                f"{base_url}/mcp/stream",
                json=init_request,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                print("   ✅ MCP stream endpoint accessible")
                # Try to parse response
                try:
                    data = response.json()
                    print(f"   Response: {json.dumps(data, indent=2)[:200]}...")
                except:
                    print(f"   Response (text): {response.text[:200]}...")
            else:
                print(f"   Status: {response.status_code}")
        except Exception as e:
            print(f"   ℹ️  Stream endpoint: {e}")
        
        # Test 4: Check SSE endpoint
        print("\n4. Testing SSE endpoint...")
        try:
            response = await client.get(
                f"{base_url}/mcp/sse",
                headers={"Accept": "text/event-stream"}
            )
            print(f"   Response status: {response.status_code}")
            if response.status_code == 200:
                print("   ✅ SSE endpoint accessible")
        except Exception as e:
            print(f"   ℹ️  SSE endpoint: {e}")

async def test_backend_services():
    """Test that backend services are accessible"""
    print("\n5. Testing backend services...")
    
    async with httpx.AsyncClient() as client:
        # Test Catalog Manager
        try:
            response = await client.get("http://localhost:8080/health")
            if response.status_code == 200:
                print("   ✅ Catalog Manager: Running")
            else:
                print("   ❌ Catalog Manager: Not healthy")
        except:
            print("   ❌ Catalog Manager: Not accessible")
        
        # Test Fault Manager
        try:
            response = await client.get("http://localhost:8081/health")
            if response.status_code == 200:
                print("   ✅ Fault Manager: Running")
            else:
                print("   ❌ Fault Manager: Not healthy")
        except:
            print("   ❌ Fault Manager: Not accessible")

async def main():
    """Run all tests"""
    await test_mcp_http_streaming()
    await test_backend_services()
    
    print("\n" + "=" * 50)
    print("✅ Testing complete!")
    print("\nIf all tests pass, you can now:")
    print("1. Copy claude_desktop_config_http.json to Claude config")
    print("2. Restart Claude Desktop")
    print("3. Connect to the MCP server")

if __name__ == "__main__":
    asyncio.run(main())
