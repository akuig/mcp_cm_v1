#!/usr/bin/env python3
"""
Comprehensive Test Suite for Telepath AI Fixes
Tests both TMF622 list handling and enhanced catalog features
"""

import requests
import json
import sys
from datetime import datetime

# Test configuration
CATALOG_MANAGER_URL = "http://localhost:8080"

def test_tmf622_order_management():
    """Test TMF622 Order Management - should return list format"""
    print("🧪 Testing TMF622 Order Management (List Format)...")
    print("-" * 50)
    
    try:
        # Test GET /tmf622/productOrder (should return array)
        response = requests.get(f"{CATALOG_MANAGER_URL}/tmf622/productOrder?limit=3")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response Type: {type(data)}")
            
            if isinstance(data, list):
                print("✅ SUCCESS: TMF622 correctly returns list format!")
                print(f"Number of orders: {len(data)}")
                if data:
                    print("Sample order structure:")
                    print(json.dumps(data[0], indent=2)[:500] + "...")
            else:
                print("❌ ISSUE: TMF622 should return list but returned dict")
                print(f"Data: {json.dumps(data, indent=2)[:200]}...")
        else:
            print(f"❌ ERROR: Status {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ EXCEPTION: {str(e)}")
    
    print("")

def test_enhanced_catalog_apis():
    """Test Enhanced Catalog APIs"""
    print("🧪 Testing Enhanced Catalog APIs...")
    print("-" * 40)
    
    # Test cases for enhanced APIs
    test_cases = [
        {
            "name": "Service Specifications",
            "url": "/api/service-specifications",
            "params": {"limit": 3}
        },
        {
            "name": "Product Offerings", 
            "url": "/api/product-offerings",
            "params": {"limit": 3}
        },
        {
            "name": "Service Coverage",
            "url": "/api/service-coverage", 
            "params": {}
        },
        {
            "name": "Recent Orders",
            "url": "/api/orders/recent",
            "params": {}
        },
        {
            "name": "All Customers",
            "url": "/api/customers",
            "params": {}
        }
    ]
    
    for test_case in test_cases:
        print(f"\n📋 Testing {test_case['name']}...")
        try:
            response = requests.get(
                f"{CATALOG_MANAGER_URL}{test_case['url']}", 
                params=test_case['params']
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ SUCCESS: {test_case['name']} working!")
                print(f"   Data type: {type(data)}")
                if isinstance(data, list):
                    print(f"   Count: {len(data)} items")
                elif isinstance(data, dict):
                    print(f"   Keys: {list(data.keys())}")
            else:
                print(f"❌ FAILED: {test_case['name']} - Status {response.status_code}")
                if response.status_code == 404:
                    print("   This enhanced API endpoint is missing")
                else:
                    print(f"   Error: {response.text[:100]}...")
                    
        except Exception as e:
            print(f"❌ EXCEPTION in {test_case['name']}: {str(e)}")

def test_core_tmf_apis():
    """Test Core TMF APIs"""
    print("🧪 Testing Core TMF APIs...")
    print("-" * 30)
    
    # Test TMF629 Customer Management
    print("\n📋 Testing TMF629 Customer Management...")
    try:
        response = requests.get(f"{CATALOG_MANAGER_URL}/tmf629/customer/8452934")
        if response.status_code == 200:
            data = response.json()
            print("✅ SUCCESS: TMF629 Customer Management working!")
            print(f"   Customer: {data.get('name', 'Unknown')}")
        else:
            print(f"❌ FAILED: TMF629 - Status {response.status_code}")
    except Exception as e:
        print(f"❌ EXCEPTION: {str(e)}")
    
    # Test TMF637 Service Qualification
    print("\n📋 Testing TMF637 Service Qualification...")
    try:
        test_payload = {
            "address": {
                "streetName": "Main St",
                "streetNumber": "123", 
                "city": "New York"
            },
            "serviceSpecification": {
                "id": "fiber-internet-basic",
                "name": "Fiber Internet Basic"
            }
        }
        
        response = requests.post(
            f"{CATALOG_MANAGER_URL}/tmf637/serviceQualification",
            json=test_payload
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ SUCCESS: TMF637 Service Qualification working!")
            result = data.get('serviceQualificationItem', [{}])[0].get('qualificationResult')
            print(f"   Result: {result}")
        else:
            print(f"❌ FAILED: TMF637 - Status {response.status_code}")
    except Exception as e:
        print(f"❌ EXCEPTION: {str(e)}")

def test_health_check():
    """Test system health"""
    print("🏥 Testing System Health...")
    print("-" * 25)
    
    try:
        response = requests.get(f"{CATALOG_MANAGER_URL}/health")
        if response.status_code == 200:
            print("✅ SUCCESS: System is healthy!")
        else:
            print(f"❌ FAILED: Health check failed - Status {response.status_code}")
    except Exception as e:
        print(f"❌ EXCEPTION: Cannot reach system - {str(e)}")
    
    print("")

def main():
    """Run all tests"""
    print("🚀 TELEPATH AI - COMPREHENSIVE FIX TESTING")
    print("=" * 50)
    print(f"Test Time: {datetime.now().isoformat()}")
    print(f"Testing against: {CATALOG_MANAGER_URL}")
    print("")
    
    # Test system health first
    test_health_check()
    
    # Test core TMF APIs 
    test_core_tmf_apis()
    
    # Test the critical TMF622 fix
    test_tmf622_order_management()
    
    # Test enhanced catalog features
    test_enhanced_catalog_apis()
    
    print("=" * 50)
    print("🎯 TEST SUMMARY")
    print("=" * 50)
    print("Key Areas Tested:")
    print("  ✓ System Health Check")
    print("  ✓ Core TMF APIs (TMF629, TMF637)")
    print("  ✓ TMF622 Order Management (List Format)")
    print("  ✓ Enhanced Catalog APIs")
    print("")
    print("🔧 Next Steps:")
    print("  1. If TMF622 returns list ✅ - Fix #1 SUCCESS")
    print("  2. If Enhanced APIs work ✅ - Fix #2 SUCCESS") 
    print("  3. Update Claude Desktop to use mcp_server_fixed.py")
    print("  4. Restart Docker containers with enhanced catalog")
    print("")

if __name__ == "__main__":
    main()
