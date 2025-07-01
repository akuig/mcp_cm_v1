#!/usr/bin/env python3
"""
Automated test script for Telepath AI MCP Server
"""

import asyncio
import json
import aiohttp
import argparse
from datetime import datetime
import sys

CATALOG_MANAGER_URL = "http://localhost:8080"

class TestRunner:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.session = None
    
    async def setup(self):
        """Setup test session"""
        self.session = aiohttp.ClientSession()
    
    async def teardown(self):
        """Cleanup test session"""
        if self.session:
            await self.session.close()
    
    async def test_service_qualification_success(self):
        """Test successful service qualification"""
        print("\n🧪 Testing Service Qualification - Success Case")
        
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
        
        async with self.session.post(
            f"{CATALOG_MANAGER_URL}/tmf637/serviceQualification",
            json=data
        ) as response:
            result = await response.json()
            
            if response.status == 200 and result['serviceQualificationItem'][0]['qualificationResult'] == 'qualified':
                print("✅ Service qualification successful")
                self.passed += 1
            else:
                print(f"❌ Service qualification failed: {result}")
                self.failed += 1
    
    async def test_service_qualification_not_available(self):
        """Test service not available"""
        print("\n🧪 Testing Service Qualification - Not Available")
        
        data = {
            "address": {
                "streetName": "Cherry Lane",
                "streetNumber": "456",
                "city": "Shelbyville"
            },
            "serviceSpecification": {
                "id": "fiber1000",
                "name": "Fiber 1 Gbps Plan"
            }
        }
        
        async with self.session.post(
            f"{CATALOG_MANAGER_URL}/tmf637/serviceQualification",
            json=data
        ) as response:
            result = await response.json()
            
            if response.status == 200 and result['serviceQualificationItem'][0]['qualificationResult'] == 'unqualified':
                print("✅ Service unavailability correctly detected")
                self.passed += 1
            else:
                print(f"❌ Unexpected result: {result}")
                self.failed += 1
    
    async def test_customer_management_success(self):
        """Test successful customer lookup"""
        print("\n🧪 Testing Customer Management - Success Case")
        
        async with self.session.get(
            f"{CATALOG_MANAGER_URL}/tmf629/customer/8452934"
        ) as response:
            result = await response.json()
            
            if (response.status == 200 and 
                result['name'] == 'Jane Doe' and 
                result['accountStatus'] == 'active' and
                result['creditScore'] == 720):
                print("✅ Customer lookup successful")
                self.passed += 1
            else:
                print(f"❌ Customer lookup failed: {result}")
                self.failed += 1
    
    async def test_customer_not_found(self):
        """Test customer not found"""
        print("\n🧪 Testing Customer Management - Not Found")
        
        async with self.session.get(
            f"{CATALOG_MANAGER_URL}/tmf629/customer/9999999"
        ) as response:
            if response.status == 404:
                print("✅ Customer not found handled correctly")
                self.passed += 1
            else:
                print(f"❌ Expected 404, got {response.status}")
                self.failed += 1
    
    async def test_product_order_creation(self):
        """Test product order creation"""
        print("\n🧪 Testing Product Order Creation")
        
        data = {
            "orderDate": datetime.now().strftime("%Y-%m-%d"),
            "externalId": f"TEST-ORDER-{datetime.now().timestamp()}",
            "relatedParty": [{
                "id": "8452934",
                "role": "customer"
            }],
            "orderItem": [{
                "action": "add",
                "productOffering": {
                    "id": "fiber500"
                },
                "product": {
                    "place": {
                        "streetNumber": "123",
                        "streetName": "Main Street",
                        "city": "Springfield"
                    }
                }
            }]
        }
        
        async with self.session.post(
            f"{CATALOG_MANAGER_URL}/tmf622/productOrder",
            json=data
        ) as response:
            result = await response.json()
            
            if response.status == 201 and 'id' in result:
                print(f"✅ Order created successfully: {result['id']}")
                self.passed += 1
                return result['id']
            else:
                print(f"❌ Order creation failed: {result}")
                self.failed += 1
                return None
    
    async def test_service_activation(self):
        """Test service activation"""
        print("\n🧪 Testing Service Activation")
        
        data = {
            "service": {
                "name": "Fiber Internet Test",
                "serviceType": "Broadband",
                "place": {
                    "streetNumber": "123",
                    "streetName": "Main Street",
                    "city": "Springfield"
                },
                "serviceSpecification": {
                    "id": "fiber500"
                }
            }
        }
        
        async with self.session.post(
            f"{CATALOG_MANAGER_URL}/tmf640/serviceActivation",
            json=data
        ) as response:
            result = await response.json()
            
            if response.status == 201 and result['service']['status'] == 'activated':
                print(f"✅ Service activated successfully: {result['id']}")
                self.passed += 1
            else:
                print(f"❌ Service activation failed: {result}")
                self.failed += 1
    
    async def test_complete_workflow(self):
        """Test complete order workflow"""
        print("\n🧪 Testing Complete Order Workflow")
        
        # Step 1: Service Qualification
        print("  Step 1: Checking service availability...")
        await self.test_service_qualification_success()
        
        # Step 2: Customer Check
        print("  Step 2: Checking customer eligibility...")
        await self.test_customer_management_success()
        
        # Step 3: Create Order
        print("  Step 3: Creating order...")
        order_id = await self.test_product_order_creation()
        
        # Step 4: Activate Service
        if order_id:
            print("  Step 4: Activating service...")
            await self.test_service_activation()
    
    async def run_all_tests(self):
        """Run all tests"""
        print("🚀 Starting Telepath AI MCP Server Tests")
        print("=" * 50)
        
        await self.setup()
        
        try:
            # Individual tests
            await self.test_service_qualification_success()
            await self.test_service_qualification_not_available()
            await self.test_customer_management_success()
            await self.test_customer_not_found()
            
            # Complete workflow
            await self.test_complete_workflow()
            
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
        """Run concurrent tests"""
        print(f"🚀 Running {count} concurrent order workflows")
        print("=" * 50)
        
        await self.setup()
        
        try:
            tasks = []
            for i in range(count):
                tasks.append(self.test_product_order_creation())
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            successful = sum(1 for r in results if r and not isinstance(r, Exception))
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
