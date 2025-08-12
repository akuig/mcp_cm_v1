#!/usr/bin/env python3
"""
Diagnostic script to test Catalog Manager endpoints and identify issues
"""

import asyncio
import aiohttp
import json
from typing import Dict, List, Tuple
from datetime import datetime

# Configuration - Update this with your actual URL
CATALOG_MANAGER_URL = "http://localhost:8080"  # Update with your ngrok URL or local URL

class CatalogDiagnostics:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = None
        self.results = []
    
    async def setup(self):
        """Initialize session"""
        self.session = aiohttp.ClientSession()
    
    async def cleanup(self):
        """Cleanup session"""
        if self.session:
            await self.session.close()
    
    async def test_endpoint(self, method: str, path: str, data: Dict = None, params: Dict = None) -> Tuple[str, int, str]:
        """Test a single endpoint"""
        url = f"{self.base_url}{path}"
        
        try:
            if method == "GET":
                async with self.session.get(url, params=params, timeout=5) as response:
                    status = response.status
                    content_type = response.headers.get('Content-Type', 'unknown')
                    
                    if 'application/json' in content_type:
                        try:
                            body = await response.json()
                            return path, status, f"JSON response with {len(body) if isinstance(body, list) else 'object'} items"
                        except:
                            return path, status, "Invalid JSON response"
                    elif 'text/html' in content_type:
                        return path, status, "HTML response (wrong content type)"
                    else:
                        return path, status, f"Response type: {content_type}"
            
            elif method == "POST":
                async with self.session.post(url, json=data, timeout=5) as response:
                    status = response.status
                    content_type = response.headers.get('Content-Type', 'unknown')
                    
                    if 'application/json' in content_type:
                        try:
                            body = await response.json()
                            return path, status, "JSON response"
                        except:
                            return path, status, "Invalid JSON response"
                    else:
                        return path, status, f"Response type: {content_type}"
        
        except asyncio.TimeoutError:
            return path, 0, "Timeout"
        except Exception as e:
            return path, 0, f"Error: {str(e)}"
    
    async def run_diagnostics(self):
        """Run all diagnostic tests"""
        print(f"\n{'='*60}")
        print(f"CATALOG MANAGER DIAGNOSTICS")
        print(f"Testing: {self.base_url}")
        print(f"Time: {datetime.now().isoformat()}")
        print(f"{'='*60}\n")
        
        # Core TMF Endpoints
        print("CORE TMF ENDPOINTS:")
        print("-" * 40)
        
        core_tests = [
            ("POST", "/tmf637/serviceQualification", {
                "address": {"streetName": "Main", "streetNumber": "123", "city": "TestCity"},
                "serviceSpecification": {"id": "fiber-100", "name": "Fiber 100Mbps"}
            }),
            ("GET", "/tmf629/customer/CUST001", None),
            ("POST", "/tmf622/productOrder", {
                "orderDate": "2025-01-01",
                "externalId": "TEST001",
                "relatedParty": [{"id": "CUST001", "role": "customer"}],
                "orderItem": [{"action": "add", "productOffering": {"id": "OFFER001"}}]
            }),
            ("POST", "/tmf640/serviceActivation", {
                "service": {
                    "name": "Test Service",
                    "serviceType": "Broadband",
                    "place": {"streetName": "Main", "streetNumber": "123", "city": "TestCity"},
                    "serviceSpecification": {"id": "fiber-100"}
                }
            })
        ]
        
        for method, path, data in core_tests:
            endpoint, status, message = await self.test_endpoint(method, path, data)
            status_icon = "✓" if status == 200 else "✗"
            print(f"{status_icon} {method:4} {endpoint:40} [{status:3}] {message}")
        
        # Enhanced Catalog Endpoints - Try multiple variations
        print("\nENHANCED CATALOG ENDPOINTS:")
        print("-" * 40)
        
        enhanced_tests = [
            # Service Specifications - Multiple possible paths
            ("GET", "/api/service-specifications", None),
            ("GET", "/tmf633/serviceSpecification", None),
            ("GET", "/service-specifications", None),
            
            # Product Offerings - Multiple possible paths
            ("GET", "/api/product-offerings", None),
            ("GET", "/tmf620/productOffering", None),
            ("GET", "/product-offerings", None),
            
            # Geographic Locations - Multiple possible paths
            ("GET", "/api/geographic-locations", None),
            ("GET", "/tmf673/geographicLocation", None),
            ("GET", "/geographic-locations", None),
            
            # Orders - Multiple possible paths
            ("GET", "/api/orders", None),
            ("GET", "/api/product-orders", None),
            ("GET", "/tmf622/productOrder", None),
            
            # Sync endpoints
            ("POST", "/api/sync", {"type": "full"}),
            ("POST", "/api/catalog/sync", {"type": "full"}),
        ]
        
        for method, path, data in enhanced_tests:
            endpoint, status, message = await self.test_endpoint(method, path, data)
            status_icon = "✓" if status in [200, 201] else "✗"
            print(f"{status_icon} {method:4} {endpoint:40} [{status:3}] {message}")
        
        # Check root endpoint for API info
        print("\nROOT ENDPOINT CHECK:")
        print("-" * 40)
        
        root_tests = [
            ("GET", "/", None),
            ("GET", "/api", None),
            ("GET", "/health", None),
            ("GET", "/api/health", None),
            ("GET", "/swagger", None),
            ("GET", "/api-docs", None),
        ]
        
        for method, path, data in root_tests:
            endpoint, status, message = await self.test_endpoint(method, path, data)
            status_icon = "✓" if status == 200 else "✗"
            print(f"{status_icon} {method:4} {endpoint:40} [{status:3}] {message}")
        
        print("\n" + "="*60)
        print("DIAGNOSTICS COMPLETE")
        print("="*60 + "\n")
    
    async def run(self):
        """Main run method"""
        await self.setup()
        try:
            await self.run_diagnostics()
        finally:
            await self.cleanup()

if __name__ == "__main__":
    import sys
    
    # Allow URL to be passed as argument
    url = sys.argv[1] if len(sys.argv) > 1 else CATALOG_MANAGER_URL
    
    print(f"Using Catalog Manager URL: {url}")
    diagnostics = CatalogDiagnostics(url)
    asyncio.run(diagnostics.run())
