#!/usr/bin/env python3
"""
Quick test script to verify all endpoints are working
"""

import requests
import json
import sys
from datetime import datetime

def test_endpoint(method, url, data=None, name=""):
    """Test a single endpoint"""
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        
        status = "✅" if response.status_code in [200, 201] else "❌"
        print(f"{status} {name}: {response.status_code}")
        
        if response.status_code not in [200, 201]:
            print(f"   Response: {response.text[:200]}")
        
        return response.status_code in [200, 201]
    except Exception as e:
        print(f"❌ {name}: Error - {str(e)}")
        return False

def main():
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8080"
    
    print(f"\n{'='*50}")
    print(f"Testing Catalog Manager at: {base_url}")
    print(f"Time: {datetime.now().isoformat()}")
    print(f"{'='*50}\n")
    
    all_passed = True
    
    # Test health
    print("Basic Health Checks:")
    all_passed &= test_endpoint("GET", f"{base_url}/health", name="Health Check")
    all_passed &= test_endpoint("GET", f"{base_url}/api", name="API Info")
    
    # Test core TMF endpoints
    print("\nCore TMF Endpoints:")
    all_passed &= test_endpoint("GET", f"{base_url}/tmf629/customer/TEST001", name="Customer Management")
    
    # Test enhanced catalog endpoints
    print("\nEnhanced Catalog Endpoints:")
    all_passed &= test_endpoint("GET", f"{base_url}/api/service-specifications", name="Service Specifications")
    all_passed &= test_endpoint("GET", f"{base_url}/api/product-offerings", name="Product Offerings")
    all_passed &= test_endpoint("GET", f"{base_url}/api/geographic-locations", name="Geographic Locations")
    all_passed &= test_endpoint("GET", f"{base_url}/api/orders", name="Order Management")
    
    print(f"\n{'='*50}")
    if all_passed:
        print("✅ ALL TESTS PASSED!")
    else:
        print("❌ Some tests failed. Check the logs above.")
    print(f"{'='*50}\n")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
