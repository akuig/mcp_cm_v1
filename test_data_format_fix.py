#!/usr/bin/env python3
"""
Test script to verify TMF622 list/dict handling fix
"""

import asyncio
import aiohttp
import json
import sys
from typing import Union, List, Dict

BASE_URL = "http://localhost:8080"

async def test_order_management():
    """Test that order_management returns correct types"""
    async with aiohttp.ClientSession() as session:
        print("🧪 Testing TMF622 Order Management Data Format Fix")
        print("=" * 50)
        
        # Test 1: List multiple orders (should return array/list)
        print("\n1️⃣ Testing list orders (should return array):")
        try:
            url = f"{BASE_URL}/tmf622/productOrder?limit=3"
            async with session.get(url) as response:
                data = await response.json()
                
                if isinstance(data, list):
                    print(f"   ✅ Correctly returned list with {len(data)} orders")
                    if data:
                        print(f"   First order ID: {data[0].get('id', 'N/A')}")
                else:
                    print(f"   ❌ ERROR: Expected list but got {type(data).__name__}")
                    return False
        except Exception as e:
            print(f"   ❌ Error testing list orders: {e}")
            return False
        
        # Test 2: Get single order (should return dict)
        print("\n2️⃣ Testing single order retrieval (should return dict):")
        if data and len(data) > 0:
            order_id = data[0].get('id')
            if order_id:
                try:
                    url = f"{BASE_URL}/tmf622/productOrder/{order_id}"
                    async with session.get(url) as response:
                        single_order = await response.json()
                        
                        if isinstance(single_order, dict):
                            print(f"   ✅ Correctly returned dict for order {order_id}")
                            print(f"   Order state: {single_order.get('state', 'N/A')}")
                        else:
                            print(f"   ❌ ERROR: Expected dict but got {type(single_order).__name__}")
                            return False
                except Exception as e:
                    print(f"   ❌ Error testing single order: {e}")
                    return False
            else:
                print("   ⚠️  No order ID found to test single retrieval")
        else:
            print("   ⚠️  No orders available to test single retrieval")
        
        # Test 3: Filter by customer (should return array/list)
        print("\n3️⃣ Testing customer filter (should return array):")
        try:
            url = f"{BASE_URL}/tmf622/productOrder?relatedParty.id=CUST001&limit=5"
            async with session.get(url) as response:
                customer_orders = await response.json()
                
                if isinstance(customer_orders, list):
                    print(f"   ✅ Correctly returned list with {len(customer_orders)} orders for CUST001")
                else:
                    print(f"   ❌ ERROR: Expected list but got {type(customer_orders).__name__}")
                    return False
        except Exception as e:
            print(f"   ❌ Error testing customer filter: {e}")
            return False
        
        print("\n" + "=" * 50)
        print("✅ All tests passed! TMF622 data format issue is FIXED")
        return True

async def test_mcp_server_health():
    """Test if MCP server is responding"""
    async with aiohttp.ClientSession() as session:
        print("\n📡 Testing MCP Server Health...")
        try:
            # Test catalog manager
            url = f"{BASE_URL}/health"
            async with session.get(url) as response:
                if response.status == 200:
                    print("   ✅ Catalog Manager is healthy")
                else:
                    print(f"   ❌ Catalog Manager returned status {response.status}")
                    
            # Note: MCP server on port 8090 uses stdio, not HTTP directly
            print("   ℹ️  MCP Server (port 8090) uses stdio protocol")
            return True
        except Exception as e:
            print(f"   ❌ Error checking health: {e}")
            return False

async def main():
    """Run all tests"""
    print("🚀 TMF622 Data Format Fix Verification")
    print("=" * 50)
    
    # Check services are running
    health_ok = await test_mcp_server_health()
    if not health_ok:
        print("\n⚠️  Services may not be running. Run: docker-compose up -d")
        sys.exit(1)
    
    # Test the fix
    success = await test_order_management()
    
    if success:
        print("\n🎉 SUCCESS: Data format issue is resolved!")
        print("\n📝 Next steps:")
        print("  1. Restart Claude Desktop to pick up changes")
        print("  2. Test order_management tool in Claude Desktop")
        print("  3. It should now handle both list and single order responses")
        sys.exit(0)
    else:
        print("\n❌ FAILED: Data format issue still present")
        print("\n🔧 To fix:")
        print("  1. Run: ./fix_data_format_issue.sh")
        print("  2. Wait for services to restart")
        print("  3. Run this test again")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
