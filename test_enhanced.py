#!/usr/bin/env python3
"""
Enhanced MCP Test Suite
Tests all the new catalog management tools and APIs
"""

import asyncio
import aiohttp
import json
import sys
from typing import Dict, Any, List
from datetime import datetime

# Configuration
CATALOG_MANAGER_URL = "http://localhost:8080"
MCP_SERVER_URL = "http://localhost:8090"
TIMEOUT = 30

class Colors:
    """ANSI color codes for terminal output"""
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    PURPLE = '\033[0;35m'
    CYAN = '\033[0;36m'
    NC = '\033[0m'  # No Color

def print_test(message: str):
    print(f"{Colors.BLUE}[TEST]{Colors.NC} {message}")

def print_success(message: str):
    print(f"{Colors.GREEN}[PASS]{Colors.NC} {message}")

def print_error(message: str):
    print(f"{Colors.RED}[FAIL]{Colors.NC} {message}")

def print_warning(message: str):
    print(f"{Colors.YELLOW}[WARN]{Colors.NC} {message}")

def print_info(message: str):
    print(f"{Colors.CYAN}[INFO]{Colors.NC} {message}")

class EnhancedMCPTester:
    def __init__(self):
        self.session = None
        self.test_results = {
            'passed': 0,
            'failed': 0,
            'warnings': 0,
            'tests': []
        }

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    def record_test(self, name: str, passed: bool, message: str = "", warning: bool = False):
        """Record test result"""
        if warning:
            self.test_results['warnings'] += 1
            status = 'warning'
        elif passed:
            self.test_results['passed'] += 1
            status = 'passed'
        else:
            self.test_results['failed'] += 1
            status = 'failed'
        
        self.test_results['tests'].append({
            'name': name,
            'status': status,
            'message': message,
            'timestamp': datetime.utcnow().isoformat()
        })

    async def test_catalog_manager_health(self):
        """Test basic catalog manager health"""
        print_test("Testing Catalog Manager health...")
        try:
            async with self.session.get(f"{CATALOG_MANAGER_URL}/health", timeout=TIMEOUT) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('status') == 'healthy':
                        print_success("Catalog Manager is healthy")
                        self.record_test("catalog_manager_health", True)
                        return True
                    else:
                        print_error(f"Catalog Manager returned unhealthy status: {data}")
                        self.record_test("catalog_manager_health", False, f"Unhealthy status: {data}")
                        return False
                else:
                    print_error(f"Catalog Manager health check failed with status {response.status}")
                    self.record_test("catalog_manager_health", False, f"HTTP {response.status}")
                    return False
        except Exception as e:
            print_error(f"Catalog Manager health check error: {str(e)}")
            self.record_test("catalog_manager_health", False, str(e))
            return False

    async def test_service_specifications_api(self):
        """Test service specifications APIs"""
        print_test("Testing Service Specifications API...")
        
        # Test GET /api/service-specifications
        try:
            async with self.session.get(f"{CATALOG_MANAGER_URL}/api/service-specifications?limit=5", timeout=TIMEOUT) as response:
                if response.status == 200:
                    data = await response.json()
                    if 'specifications' in data and isinstance(data['specifications'], list):
                        print_success(f"Retrieved {len(data['specifications'])} service specifications")
                        self.record_test("list_service_specifications", True, f"Found {len(data['specifications'])} specs")
                        
                        # Test filtering
                        if data['specifications']:
                            first_spec = data['specifications'][0]
                            print_info(f"Sample spec: {first_spec.get('name')} ({first_spec.get('service_type')})")
                    else:
                        print_error("Invalid response format for service specifications")
                        self.record_test("list_service_specifications", False, "Invalid response format")
                        return False
                else:
                    print_error(f"Service specifications API failed with status {response.status}")
                    self.record_test("list_service_specifications", False, f"HTTP {response.status}")
                    return False
        except Exception as e:
            print_error(f"Service specifications API error: {str(e)}")
            self.record_test("list_service_specifications", False, str(e))
            return False

        # Test POST /api/service-specifications (create new spec)
        test_spec = {
            "name": "Test Enhanced Fiber",
            "service_type": "fiber_internet",
            "description": "Enhanced fiber service for automated testing"
        }
        
        try:
            async with self.session.post(f"{CATALOG_MANAGER_URL}/api/service-specifications", 
                                       json=test_spec, timeout=TIMEOUT) as response:
                if response.status == 201:
                    data = await response.json()
                    print_success(f"Created service specification: {data.get('name')} (ID: {data.get('id')})")
                    self.record_test("create_service_specification", True, f"Created spec ID: {data.get('id')}")
                    return data.get('id')  # Return ID for linking tests
                else:
                    print_error(f"Service specification creation failed with status {response.status}")
                    text = await response.text()
                    self.record_test("create_service_specification", False, f"HTTP {response.status}: {text}")
                    return None
        except Exception as e:
            print_error(f"Service specification creation error: {str(e)}")
            self.record_test("create_service_specification", False, str(e))
            return None

    async def test_product_offerings_api(self):
        """Test product offerings APIs"""
        print_test("Testing Product Offerings API...")
        
        # Test GET /api/product-offerings
        try:
            async with self.session.get(f"{CATALOG_MANAGER_URL}/api/product-offerings?category=internet&include_services=true&limit=3", timeout=TIMEOUT) as response:
                if response.status == 200:
                    data = await response.json()
                    if 'offerings' in data and isinstance(data['offerings'], list):
                        print_success(f"Retrieved {len(data['offerings'])} product offerings")
                        self.record_test("list_product_offerings", True, f"Found {len(data['offerings'])} offerings")
                        
                        # Check if linked services are included
                        if data['offerings']:
                            first_offering = data['offerings'][0]
                            print_info(f"Sample offering: {first_offering.get('name')} (${first_offering.get('price_monthly')}/month)")
                            if 'linked_services' in first_offering:
                                print_info(f"Linked services: {len(first_offering.get('linked_services', []))}")
                    else:
                        print_error("Invalid response format for product offerings")
                        self.record_test("list_product_offerings", False, "Invalid response format")
                        return False
                else:
                    print_error(f"Product offerings API failed with status {response.status}")
                    self.record_test("list_product_offerings", False, f"HTTP {response.status}")
                    return False
        except Exception as e:
            print_error(f"Product offerings API error: {str(e)}")
            self.record_test("list_product_offerings", False, str(e))
            return False

        # Test POST /api/product-offerings (create new offering)
        test_offering = {
            "name": "Test Premium Package",
            "description": "Premium package for automated testing",
            "category": "internet",
            "price_monthly": 299.99,
            "price_setup": 199.99,
            "contract_length_months": 12
        }
        
        try:
            async with self.session.post(f"{CATALOG_MANAGER_URL}/api/product-offerings", 
                                       json=test_offering, timeout=TIMEOUT) as response:
                if response.status == 201:
                    data = await response.json()
                    print_success(f"Created product offering: {data.get('name')} (ID: {data.get('id')})")
                    self.record_test("create_product_offering", True, f"Created offering ID: {data.get('id')}")
                    return data.get('id')  # Return ID for linking tests
                else:
                    print_error(f"Product offering creation failed with status {response.status}")
                    text = await response.text()
                    self.record_test("create_product_offering", False, f"HTTP {response.status}: {text}")
                    return None
        except Exception as e:
            print_error(f"Product offering creation error: {str(e)}")
            self.record_test("create_product_offering", False, str(e))
            return None

    async def test_geographic_locations_api(self):
        """Test geographic locations APIs"""
        print_test("Testing Geographic Locations API...")
        
        # Test GET /api/geographic-locations
        try:
            async with self.session.get(f"{CATALOG_MANAGER_URL}/api/geographic-locations?city=Springfield&include_coverage=true&limit=3", timeout=TIMEOUT) as response:
                if response.status == 200:
                    data = await response.json()
                    if 'locations' in data and isinstance(data['locations'], list):
                        print_success(f"Retrieved {len(data['locations'])} geographic locations")
                        self.record_test("list_geographic_locations", True, f"Found {len(data['locations'])} locations")
                        
                        # Check coverage details
                        if data['locations']:
                            first_location = data['locations'][0]
                            print_info(f"Sample location: {first_location.get('street_name')}, {first_location.get('city')}")
                            coverage_details = first_location.get('coverage_details', [])
                            print_info(f"Coverage services: {len(coverage_details)}")
                            return first_location.get('location_id')  # Return for coverage tests
                    else:
                        print_error("Invalid response format for geographic locations")
                        self.record_test("list_geographic_locations", False, "Invalid response format")
                        return None
                else:
                    print_error(f"Geographic locations API failed with status {response.status}")
                    self.record_test("list_geographic_locations", False, f"HTTP {response.status}")
                    return None
        except Exception as e:
            print_error(f"Geographic locations API error: {str(e)}")
            self.record_test("list_geographic_locations", False, str(e))
            return None

    async def test_linking_api(self, offering_id: str, spec_id: str):
        """Test linking product offerings to service specifications"""
        if not offering_id or not spec_id:
            print_warning("Skipping linking test - missing offering or spec ID")
            self.record_test("link_offering_to_specification", False, "Missing IDs", warning=True)
            return
        
        print_test("Testing Offering-to-Specification Linking...")
        
        link_data = {
            "product_offering_id": offering_id,
            "service_specification_id": spec_id,
            "is_primary": True
        }
        
        try:
            async with self.session.post(f"{CATALOG_MANAGER_URL}/api/link-offering-to-specification", 
                                       json=link_data, timeout=TIMEOUT) as response:
                if response.status == 201:
                    data = await response.json()
                    print_success(f"Successfully linked offering {offering_id} to specification {spec_id}")
                    self.record_test("link_offering_to_specification", True, f"Linked {offering_id} to {spec_id}")
                else:
                    text = await response.text()
                    print_error(f"Linking failed with status {response.status}: {text}")
                    self.record_test("link_offering_to_specification", False, f"HTTP {response.status}")
        except Exception as e:
            print_error(f"Linking API error: {str(e)}")
            self.record_test("link_offering_to_specification", False, str(e))

    async def test_coverage_api(self, location_id: str):
        """Test adding geographic coverage"""
        if not location_id:
            print_warning("Skipping coverage test - missing location ID")
            self.record_test("add_geographic_coverage", False, "Missing location ID", warning=True)
            return
        
        print_test("Testing Geographic Coverage API...")
        
        coverage_data = {
            "location_id": location_id,
            "service_type": "fiber_internet",
            "available": True,
            "max_speed_mbps": 5000,
            "coverage_quality": "excellent",
            "technology": "fiber",
            "signal_strength": 5
        }
        
        try:
            async with self.session.post(f"{CATALOG_MANAGER_URL}/api/add-geographic-coverage", 
                                       json=coverage_data, timeout=TIMEOUT) as response:
                if response.status == 201:
                    data = await response.json()
                    print_success(f"Successfully added coverage for location {location_id}")
                    self.record_test("add_geographic_coverage", True, f"Added coverage for {location_id}")
                else:
                    text = await response.text()
                    print_error(f"Coverage addition failed with status {response.status}: {text}")
                    self.record_test("add_geographic_coverage", False, f"HTTP {response.status}")
        except Exception as e:
            print_error(f"Coverage API error: {str(e)}")
            self.record_test("add_geographic_coverage", False, str(e))

    async def test_sync_catalog_api(self):
        """Test catalog sync and integrity checking"""
        print_test("Testing Catalog Sync API...")
        
        sync_data = {
            "sync_type": "integrity_check"
        }
        
        try:
            async with self.session.post(f"{CATALOG_MANAGER_URL}/api/sync-catalog-data", 
                                       json=sync_data, timeout=TIMEOUT) as response:
                if response.status == 200:
                    data = await response.json()
                    print_success(f"Catalog sync completed successfully")
                    print_info(f"Processed: {data.get('total_processed', 0)} records")
                    print_info(f"Errors: {data.get('total_errors', 0)}")
                    
                    # Check results
                    results = data.get('results', {})
                    for check_type, result in results.items():
                        status = result.get('status', 'unknown')
                        count = result.get('count', 0)
                        print_info(f"  {check_type}: {status} ({count} items)")
                    
                    self.record_test("sync_catalog_data", True, f"Synced {data.get('total_processed', 0)} records")
                else:
                    text = await response.text()
                    print_error(f"Catalog sync failed with status {response.status}: {text}")
                    self.record_test("sync_catalog_data", False, f"HTTP {response.status}")
        except Exception as e:
            print_error(f"Catalog sync API error: {str(e)}")
            self.record_test("sync_catalog_data", False, str(e))

    async def test_mcp_tools(self):
        """Test MCP server tools"""
        print_test("Testing MCP Server Tools...")
        
        # Test tools list
        try:
            tools_request = {
                "jsonrpc": "2.0",
                "method": "tools/list",
                "params": {},
                "id": 1
            }
            
            async with self.session.post(f"{MCP_SERVER_URL}/mcp/stream", 
                                       json=tools_request, 
                                       headers={"Content-Type": "application/json", "Accept": "application/json-stream"},
                                       timeout=TIMEOUT) as response:
                if response.status == 200:
                    data = await response.json()
                    if 'result' in data and 'tools' in data['result']:
                        tools = data['result']['tools']
                        print_success(f"MCP Server has {len(tools)} tools available")
                        
                        # Check for enhanced tools
                        tool_names = [tool['name'] for tool in tools]
                        enhanced_tools = [
                            'list_service_specifications',
                            'list_product_offerings', 
                            'list_geographic_locations',
                            'sync_catalog_data',
                            'create_service_specification',
                            'create_product_offering',
                            'link_offering_to_specification',
                            'add_geographic_coverage'
                        ]
                        
                        found_enhanced = sum(1 for tool in enhanced_tools if tool in tool_names)
                        print_info(f"Enhanced tools found: {found_enhanced}/{len(enhanced_tools)}")
                        
                        if found_enhanced == len(enhanced_tools):
                            print_success("All enhanced tools are available")
                            self.record_test("mcp_tools_availability", True, f"All {len(enhanced_tools)} enhanced tools available")
                        else:
                            missing = [tool for tool in enhanced_tools if tool not in tool_names]
                            print_warning(f"Missing enhanced tools: {missing}")
                            self.record_test("mcp_tools_availability", False, f"Missing tools: {missing}", warning=True)
                    else:
                        print_error("Invalid MCP tools response format")
                        self.record_test("mcp_tools_availability", False, "Invalid response format")
                else:
                    print_error(f"MCP tools list failed with status {response.status}")
                    self.record_test("mcp_tools_availability", False, f"HTTP {response.status}")
        except Exception as e:
            print_error(f"MCP tools test error: {str(e)}")
            self.record_test("mcp_tools_availability", False, str(e))

    async def run_all_tests(self):
        """Run the complete test suite"""
        print(f"{Colors.PURPLE}{'=' * 60}{Colors.NC}")
        print(f"{Colors.PURPLE}🧪 Enhanced Telecom MCP Test Suite{Colors.NC}")
        print(f"{Colors.PURPLE}{'=' * 60}{Colors.NC}")
        print()

        # Test basic health
        if not await self.test_catalog_manager_health():
            print_error("Catalog Manager is not healthy - stopping tests")
            return False

        # Test enhanced APIs
        spec_id = await self.test_service_specifications_api()
        offering_id = await self.test_product_offerings_api()
        location_id = await self.test_geographic_locations_api()
        
        # Test linking if we have both IDs
        await self.test_linking_api(offering_id, spec_id)
        
        # Test coverage if we have location ID
        await self.test_coverage_api(location_id)
        
        # Test catalog sync
        await self.test_sync_catalog_api()
        
        # Test MCP tools
        await self.test_mcp_tools()

        # Print summary
        print()
        print(f"{Colors.PURPLE}{'=' * 60}{Colors.NC}")
        print(f"{Colors.PURPLE}📊 Test Results Summary{Colors.NC}")
        print(f"{Colors.PURPLE}{'=' * 60}{Colors.NC}")
        print(f"{Colors.GREEN}✅ Passed: {self.test_results['passed']}{Colors.NC}")
        print(f"{Colors.RED}❌ Failed: {self.test_results['failed']}{Colors.NC}")
        print(f"{Colors.YELLOW}⚠️  Warnings: {self.test_results['warnings']}{Colors.NC}")
        
        total_tests = self.test_results['passed'] + self.test_results['failed'] + self.test_results['warnings']
        success_rate = (self.test_results['passed'] / total_tests * 100) if total_tests > 0 else 0
        print(f"📈 Success Rate: {success_rate:.1f}%")
        
        print()
        if self.test_results['failed'] == 0:
            print(f"{Colors.GREEN}🎉 All critical tests passed!{Colors.NC}")
            return True
        else:
            print(f"{Colors.RED}🔥 {self.test_results['failed']} test(s) failed{Colors.NC}")
            print("Failed tests:")
            for test in self.test_results['tests']:
                if test['status'] == 'failed':
                    print(f"  - {test['name']}: {test['message']}")
            return False

async def main():
    """Main test function"""
    try:
        async with EnhancedMCPTester() as tester:
            success = await tester.run_all_tests()
            sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Tests interrupted by user{Colors.NC}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}Test suite error: {str(e)}{Colors.NC}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
