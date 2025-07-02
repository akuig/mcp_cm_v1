#!/usr/bin/env python3
"""
Automated test script for Telepath AI MCP Server with HTTP streaming transport
"""

import asyncio
import json
import aiohttp
import argparse
from datetime import datetime
import sys
from typing import Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CATALOG_MANAGER_URL = "http://localhost:8080"
MCP_SERVER_URL = "http://localhost:8090"

class StreamingMCPClient:
    """MCP client for testing HTTP streaming transport"""
    
    def __init__(self, server_url: str):
        self.server_url = server_url
        self.session = None
        self.request_id = 0
    
    async def setup(self):
        """Setup HTTP session"""
        self.session = aiohttp.ClientSession()
        # Initialize the MCP connection
        await self.initialize()
    
    async def teardown(self):
        """Cleanup HTTP session"""
        if self.session:
            await self.session.close()
    
    async def send_request(self, method: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Send a request to the MCP streaming endpoint"""
        self.request_id += 1
        
        request_data = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or {},
            "id": self.request_id
        }
        
        try:
            async with self.session.post(
                f"{self.server_url}/mcp/stream",
                json=request_data,
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
                        result = json.loads(line)
                        if "error" in result:
                            logger.error(f"MCP Error: {result['error']}")
                            return {"error": result["error"]}
                        return result.get("result", {})
                
                return {"error": "No response received"}
                
        except Exception as e:
            logger.error(f"HTTP Error: {str(e)}")
            return {"error": str(e)}
    
    async def initialize(self):
        """Initialize MCP connection"""
        result = await self.send_request("initialize")
        if "error" not in result:
            logger.info(f"MCP initialized: {result.get('serverInfo', {}).get('name')} v{result.get('serverInfo', {}).get('version')}")
        return result
    
    async def list_tools(self) -> Dict[str, Any]:
        """List available MCP tools"""
        return await self.send_request("tools/list")
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call an MCP tool"""
        params = {
            "name": tool_name,
            "arguments": arguments
        }
        result = await self.send_request("tools/call", params)
        
        # Parse the tool result
        if "content" in result:
            try:
                # The content contains an array of content items
                content_items = result.get("content", [])
                if content_items and len(content_items) > 0:
                    # Get the text from the first content item
                    text_content = content_items[0].get("text", "{}")
                    # Parse the JSON string containing the actual result
                    return json.loads(text_content)
                return {}
            except json.JSONDecodeError:
                return result
        
        return result

class TestRunner:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.catalog_session = None
        self.mcp_client = None
    
    async def setup(self):
        """Setup test environment"""
        self.catalog_session = aiohttp.ClientSession()
        self.mcp_client = StreamingMCPClient(MCP_SERVER_URL)
        
        # Wait for services to be ready
        await self.wait_for_services()
        
        # Setup MCP client
        await self.mcp_client.setup()
    
    async def teardown(self):
        """Cleanup test environment"""
        if self.catalog_session:
            await self.catalog_session.close()
        if self.mcp_client:
            await self.mcp_client.teardown()
    
    async def wait_for_services(self, timeout=30):
        """Wait for both services to be ready"""
        start_time = datetime.now()
        
        while (datetime.now() - start_time).seconds < timeout:
            try:
                # Check Catalog Manager
                async with self.catalog_session.get(f"{CATALOG_MANAGER_URL}/health") as resp:
                    if resp.status == 200:
                        catalog_ready = True
                    else:
                        catalog_ready = False
                
                # Check MCP Server
                async with self.catalog_session.get(f"{MCP_SERVER_URL}/health") as resp:
                    if resp.status == 200:
                        mcp_ready = True
                    else:
                        mcp_ready = False
                
                if catalog_ready and mcp_ready:
                    logger.info("✅ All services are ready")
                    return
                    
            except Exception:
                pass
            
            await asyncio.sleep(1)
        
        raise TimeoutError("Services did not become ready in time")
    
    async def test_mcp_tools_list(self):
        """Test listing available MCP tools"""
        print("\n🧪 Testing MCP Tools List")
        
        result = await self.mcp_client.list_tools()
        
        if "error" not in result and "tools" in result:
            tools = result["tools"]
            expected_tools = ["service_qualification", "customer_management", 
                            "product_ordering", "service_activation"]
            
            found_tools = [tool["name"] for tool in tools]
            
            if all(tool in found_tools for tool in expected_tools):
                print(f"✅ Found all expected tools: {', '.join(found_tools)}")
                self.passed += 1
            else:
                print(f"❌ Missing tools. Found: {found_tools}")
                self.failed += 1
        else:
            print(f"❌ Failed to list tools: {result}")
            self.failed += 1
    
    async def test_service_qualification_via_mcp(self):
        """Test service qualification through MCP"""
        print("\n🧪 Testing Service Qualification via MCP")
        
        arguments = {
            "address": {
                "streetName": "Main Street",
                "streetNumber": "123",
                "city": "Springfield"
            },
            "serviceSpecification": {
                "id": "fiber500",
                "name": "Fiber 500 Mbps Plan"
            }
        }
        
        result = await self.mcp_client.call_tool("service_qualification", arguments)
        
        if "error" not in result:
            if result.get('serviceQualificationItem', [{}])[0].get('qualificationResult') == 'qualified':
                print("✅ Service qualification successful via MCP")
                self.passed += 1
            else:
                print(f"❌ Unexpected qualification result: {result}")
                self.failed += 1
        else:
            print(f"❌ MCP call failed: {result}")
            self.failed += 1
    
    async def test_customer_management_via_mcp(self):
        """Test customer management through MCP"""
        print("\n🧪 Testing Customer Management via MCP")
        
        arguments = {
            "customerId": "8452934"
        }
        
        result = await self.mcp_client.call_tool("customer_management", arguments)
        
        if "error" not in result:
            if result.get('name') == 'Jane Doe' and result.get('creditScore') == 720:
                print("✅ Customer lookup successful via MCP")
                self.passed += 1
            else:
                print(f"❌ Unexpected customer data: {result}")
                self.failed += 1
        else:
            print(f"❌ MCP call failed: {result}")
            self.failed += 1
    
    async def test_complete_workflow_via_mcp(self):
        """Test complete order workflow through MCP"""
        print("\n🧪 Testing Complete Workflow via MCP")
        
        # Step 1: Service Qualification
        print("  Step 1: Checking service availability via MCP...")
        qual_args = {
            "address": {
                "streetName": "Oak Avenue",
                "streetNumber": "456",
                "city": "Springfield"
            },
            "serviceSpecification": {
                "id": "fiber500",
                "name": "Fiber 500 Mbps Plan"
            }
        }
        
        result = await self.mcp_client.call_tool("service_qualification", qual_args)
        if "error" in result or result.get('serviceQualificationItem', [{}])[0].get('qualificationResult') != 'qualified':
            print(f"  ❌ Service qualification failed: {result}")
            self.failed += 1
            return
        else:
            print("  ✅ Service qualification passed")
        
        # Step 2: Customer Check
        print("  Step 2: Checking customer via MCP...")
        cust_args = {"customerId": "8452936"}  # Alice Johnson
        
        result = await self.mcp_client.call_tool("customer_management", cust_args)
        if "error" in result or result.get('accountStatus') != 'active':
            print(f"  ❌ Customer check failed: {result}")
            self.failed += 1
            return
        else:
            print("  ✅ Customer check passed")
        
        # Step 3: Create Order
        print("  Step 3: Creating order via MCP...")
        order_args = {
            "orderDate": datetime.now().strftime("%Y-%m-%d"),
            "externalId": f"MCP-TEST-{datetime.now().timestamp()}",
            "customerId": "8452936",
            "productOfferingId": "fiber500",
            "address": {
                "streetName": "Oak Avenue",
                "streetNumber": "456",
                "city": "Springfield"
            }
        }
        
        result = await self.mcp_client.call_tool("product_ordering", order_args)
        if "error" in result or "id" not in result:
            print(f"  ❌ Order creation failed: {result}")
            self.failed += 1
            return
        else:
            print(f"  ✅ Order created successfully: {result.get('id')}")
        
        # Step 4: Activate Service
        print("  Step 4: Activating service via MCP...")
        activation_args = {
            "serviceName": "Fiber Internet MCP Test",
            "serviceType": "Broadband",
            "address": {
                "streetNumber": "456",
                "streetName": "Oak Avenue",
                "city": "Springfield"
            },
            "serviceSpecificationId": "fiber500"
        }
        
        result = await self.mcp_client.call_tool("service_activation", activation_args)
        if "error" in result or result.get('service', {}).get('status') != 'activated':
            print(f"  ❌ Service activation failed: {result}")
            self.failed += 1
        else:
            print(f"  ✅ Service activated successfully: {result.get('id')}")
            self.passed += 1
    
    async def test_streaming_response(self):
        """Test that responses are properly streamed"""
        print("\n🧪 Testing Streaming Response")
        
        # Make a direct streaming request
        request_data = {
            "jsonrpc": "2.0",
            "method": "tools/list",
            "params": {},
            "id": 999
        }
        
        try:
            async with self.catalog_session.post(
                f"{MCP_SERVER_URL}/mcp/stream",
                json=request_data,
                headers={"Accept": "application/json-stream"}
            ) as response:
                if response.headers.get('Transfer-Encoding') == 'chunked':
                    print("✅ Response is using chunked transfer encoding")
                    self.passed += 1
                else:
                    print("❌ Response is not using chunked transfer encoding")
                    self.failed += 1
        except Exception as e:
            print(f"❌ Streaming test failed: {e}")
            self.failed += 1
    
    async def test_direct_catalog_apis(self):
        """Test direct catalog manager APIs"""
        print("\n🧪 Testing Direct Catalog Manager APIs")
        
        # Test service qualification
        data = {
            "address": {
                "streetName": "Main Street",
                "streetNumber": "123",
                "city": "Springfield"
            },
            "serviceSpecification": {
                "id": "fiber500",
                "name": "Fiber 500 Mbps Plan"
            }
        }
        
        async with self.catalog_session.post(
            f"{CATALOG_MANAGER_URL}/tmf637/serviceQualification",
            json=data
        ) as response:
            if response.status == 200:
                print("✅ Direct API test passed")
                self.passed += 1
            else:
                print(f"❌ Direct API test failed: {response.status}")
                self.failed += 1
    
    async def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting Telepath AI MCP Server Tests (HTTP Streaming Transport)")
        print("=" * 50)
        
        await self.setup()
        
        try:
            # Test MCP functionality
            await self.test_mcp_tools_list()
            await self.test_service_qualification_via_mcp()
            await self.test_customer_management_via_mcp()
            await self.test_streaming_response()
            await self.test_complete_workflow_via_mcp()
            
            # Test direct APIs
            await self.test_direct_catalog_apis()
            
        finally:
            await self.teardown()
        
        # Print summary
        print("\n" + "=" * 50)
        print(f"📊 Test Summary:")
        print(f"   ✅ Passed: {self.passed}")
        print(f"   ❌ Failed: {self.failed}")
        print(f"   📈 Total: {self.passed + self.failed}")
        
        return self.failed == 0
    
    async def run_concurrent_tests(self, count):
        """Run concurrent tests via MCP"""
        print(f"🚀 Running {count} concurrent MCP operations")
        print("=" * 50)
        
        await self.setup()
        
        try:
            tasks = []
            for i in range(count):
                order_args = {
                    "orderDate": datetime.now().strftime("%Y-%m-%d"),
                    "externalId": f"CONCURRENT-{i}-{datetime.now().timestamp()}",
                    "customerId": "8452934",
                    "productOfferingId": "fiber500",
                    "address": {
                        "streetName": "Main Street",
                        "streetNumber": str(100 + i),
                        "city": "Springfield"
                    }
                }
                tasks.append(self.mcp_client.call_tool("product_ordering", order_args))
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            successful = sum(1 for r in results if not isinstance(r, Exception) and "error" not in r and "id" in r)
            print(f"\n✅ Successful orders: {successful}/{count}")
            
        finally:
            await self.teardown()

async def main():
    parser = argparse.ArgumentParser(description='Test Telepath AI MCP Server')
    parser.add_argument('--concurrent', type=int, help='Run concurrent tests')
    args = parser.parse_args()
    
    runner = TestRunner()
    
    if args.concurrent:
        await runner.run_concurrent_tests(args.concurrent)
    else:
        success = await runner.run_all_tests()
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())
