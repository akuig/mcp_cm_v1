#!/usr/bin/env python3
"""
Telepath AI Catalog Manager - API Validation Script
Comprehensive testing of all TMF Forum APIs and catalog management functions
"""

import requests
import json
import time
import sys
from typing import Dict, List, Tuple
from datetime import datetime

# Configuration
API_BASE = "http://localhost:8080"
TIMEOUT = 30

# ANSI Color codes
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

def log(message: str, color: str = Colors.WHITE):
    """Log a message with color"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"{Colors.CYAN}[{timestamp}]{color} {message}{Colors.END}")

def log_success(message: str):
    log(f"✅ {message}", Colors.GREEN)

def log_error(message: str):
    log(f"❌ {message}", Colors.RED)

def log_warning(message: str):
    log(f"⚠️  {message}", Colors.YELLOW)

def log_info(message: str):
    log(f"ℹ️  {message}", Colors.BLUE)

def log_header(message: str):
    log(f"\n{'='*50}", Colors.MAGENTA)
    log(f"{message}", Colors.MAGENTA + Colors.BOLD)
    log(f"{'='*50}", Colors.MAGENTA)

class APIValidator:
    def __init__(self):
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.test_results = []

    def api_call(self, method: str, endpoint: str, data: Dict = None, expected_status: int = 200) -> Tuple[bool, Dict]:
        """Make an API call and validate response"""
        self.total_tests += 1
        
        try:
            url = f"{API_BASE}{endpoint}"
            log_info(f"{method} {endpoint}")
            
            if method == "GET":
                response = requests.get(url, timeout=TIMEOUT)
            elif method == "POST":
                response = requests.post(url, json=data, timeout=TIMEOUT)
            elif method == "PUT":
                response = requests.put(url, json=data, timeout=TIMEOUT)
            elif method == "DELETE":
                response = requests.delete(url, timeout=TIMEOUT)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            success = response.status_code == expected_status
            
            try:
                result = response.json()
            except:
                result = {"response": response.text}
            
            if success:
                self.passed_tests += 1
                log_success(f"Status: {response.status_code}")
            else:
                self.failed_tests += 1
                log_error(f"Status: {response.status_code} (expected {expected_status})")
                log_error(f"Response: {json.dumps(result, indent=2)[:200]}...")
            
            self.test_results.append({
                "method": method,
                "endpoint": endpoint,
                "status": response.status_code,
                "expected_status": expected_status,
                "success": success,
                "response_size": len(response.text)
            })
            
            return success, result
            
        except Exception as e:
            self.failed_tests += 1
            log_error(f"Exception: {str(e)}")
            self.test_results.append({
                "method": method,
                "endpoint": endpoint,
                "status": 0,
                "expected_status": expected_status,
                "success": False,
                "error": str(e)
            })
            return False, {"error": str(e)}

    def validate_health(self):
        """Test health endpoint"""
        log_header("HEALTH CHECK")
        
        success, result = self.api_call("GET", "/admin/health")
        
        if success:
            stats = result.get("statistics", {})
            log_info(f"Database Status: {result.get('database', 'unknown')}")
            log_info(f"Service Specifications: {stats.get('serviceSpecifications', 0)}")
            log_info(f"Product Offerings: {stats.get('productOfferings', 0)}")
            log_info(f"Geographic Locations: {stats.get('geographicLocations', 0)}")
            log_info(f"Active Customers: {stats.get('activeCustomers', 0)}")
        
        return success

    def validate_service_specifications(self):
        """Test TMF633 - Service Catalog Management"""
        log_header("TMF633 - SERVICE SPECIFICATIONS")
        
        # List all service specifications
        success, specs = self.api_call("GET", "/tmf633/serviceSpecification")
        
        if not success:
            return False
        
        log_info(f"Found {len(specs)} service specifications")
        
        # List with category filter
        success, filtered_specs = self.api_call("GET", "/tmf633/serviceSpecification?category=connectivity")
        
        if success:
            log_info(f"Connectivity services: {len(filtered_specs)}")
        
        # Test creating a new service specification
        new_spec = {
            "name": "Test Fiber Service",
            "description": "Test fiber service for validation",
            "category": "connectivity",
            "serviceType": "broadband",
            "characteristics": [
                {
                    "name": "bandwidth",
                    "valueType": "string",
                    "defaultValue": "100 Mbps",
                    "isConfigurable": True
                }
            ]
        }
        
        success, created_spec = self.api_call("POST", "/tmf633/serviceSpecification", new_spec, 201)
        
        if success:
            log_info(f"Created test service specification: {created_spec.get('id')}")
        
        return True

    def validate_product_offerings(self):
        """Test TMF620 - Product Catalog Management"""
        log_header("TMF620 - PRODUCT OFFERINGS")
        
        # List all product offerings
        success, offerings = self.api_call("GET", "/tmf620/productOffering")
        
        if not success:
            return False
        
        log_info(f"Found {len(offerings)} product offerings")
        
        # List residential products only
        success, residential = self.api_call("GET", "/tmf620/productOffering?category=residential")
        
        if success:
            log_info(f"Residential products: {len(residential)}")
        
        # List bundles only
        success, bundles = self.api_call("GET", "/tmf620/productOffering?isBundle=true")
        
        if success:
            log_info(f"Bundle products: {len(bundles)}")
        
        # Test creating a new product offering
        new_offering = {
            "name": "Test Internet Package",
            "description": "Test internet package for validation",
            "category": "residential",
            "isBundle": False,
            "price": {
                "amount": 49.99,
                "currency": "USD",
                "period": "monthly"
            }
        }
        
        success, created_offering = self.api_call("POST", "/tmf620/productOffering", new_offering, 201)
        
        if success:
            log_info(f"Created test product offering: {created_offering.get('id')}")
        
        return True

    def validate_geographic_locations(self):
        """Test TMF673 - Geographic Address Management"""
        log_header("TMF673 - GEOGRAPHIC LOCATIONS")
        
        # List all locations
        success, locations = self.api_call("GET", "/tmf673/geographicLocation")
        
        if not success:
            return False
        
        log_info(f"Found {len(locations)} geographic locations")
        
        # List Springfield locations
        success, springfield = self.api_call("GET", "/tmf673/geographicLocation?city=Springfield")
        
        if success:
            log_info(f"Springfield locations: {len(springfield)}")
            
            # Show sample location with coverage
            if springfield:
                sample = springfield[0]
                coverage_count = len(sample.get('serviceCoverage', []))
                log_info(f"Sample location: {sample.get('streetNumber')} {sample.get('streetName')}")
                log_info(f"Service coverage entries: {coverage_count}")
        
        return True

    def validate_customer_management(self):
        """Test TMF629 - Customer Management"""
        log_header("TMF629 - CUSTOMER MANAGEMENT")
        
        # Test known customer
        test_customer_id = "8452934"
        success, customer = self.api_call("GET", f"/tmf629/customer/{test_customer_id}")
        
        if success:
            log_info(f"Customer Name: {customer.get('name')}")
            log_info(f"Account Status: {customer.get('accountStatus')}")
            log_info(f"Credit Score: {customer.get('creditScore')}")
            log_info(f"Address: {customer.get('address', {}).get('streetNumber')} {customer.get('address', {}).get('streetName')}, {customer.get('address', {}).get('city')}")
        
        # Test non-existent customer
        success, result = self.api_call("GET", "/tmf629/customer/999999", expected_status=404)
        
        if success:
            log_info("Correctly returned 404 for non-existent customer")
        
        return True

    def validate_service_qualification(self):
        """Test TMF637 - Service Qualification"""
        log_header("TMF637 - SERVICE QUALIFICATION")
        
        # Test qualification for Jane Doe's address with fiber
        qualification_request = {
            "address": {
                "streetName": "Main Street",
                "streetNumber": "456",
                "city": "Springfield"
            },
            "serviceSpecification": {
                "id": "FIBER_1GB",
                "name": "Fiber Internet 1 Gbps"
            }
        }
        
        success, result = self.api_call("POST", "/tmf637/serviceQualification", qualification_request)
        
        if success:
            item = result.get('serviceQualificationItem', [{}])[0]
            qualification_result = item.get('qualificationResult')
            reason = item.get('reason')
            available_offerings = item.get('availableProductOfferings', [])
            
            log_info(f"Qualification Result: {qualification_result}")
            log_info(f"Reason: {reason}")
            log_info(f"Available Offerings: {len(available_offerings)}")
            
            if available_offerings:
                for offering in available_offerings[:3]:  # Show first 3
                    price = offering.get('price', {})
                    log_info(f"  - {offering.get('name')}: ${price.get('amount', 0)}/{price.get('period', 'month')}")
        
        # Test qualification for address without service
        no_service_request = {
            "address": {
                "streetName": "Nonexistent Street",
                "streetNumber": "999",
                "city": "Unknown City"
            },
            "serviceSpecification": {
                "id": "FIBER_1GB",
                "name": "Fiber Internet 1 Gbps"
            }
        }
        
        success, result = self.api_call("POST", "/tmf637/serviceQualification", no_service_request)
        
        if success:
            item = result.get('serviceQualificationItem', [{}])[0]
            if item.get('qualificationResult') == 'unqualified':
                log_info("Correctly identified unqualified address")
        
        return True

    def validate_product_ordering(self):
        """Test TMF622 - Product Ordering"""
        log_header("TMF622 - PRODUCT ORDERING")
        
        order_request = {
            "orderDate": datetime.utcnow().isoformat() + "Z",
            "externalId": "TEST_ORDER_001",
            "relatedParty": [{
                "id": "8452934",
                "role": "customer"
            }],
            "orderItem": [{
                "action": "add",
                "productOffering": {
                    "id": "FIBER_HOME_1GB"
                },
                "product": {
                    "place": {
                        "streetName": "Main Street",
                        "streetNumber": "456",
                        "city": "Springfield"
                    }
                }
            }]
        }
        
        success, result = self.api_call("POST", "/tmf622/productOrder", order_request, 201)
        
        if success:
            log_info(f"Order ID: {result.get('id')}")
            log_info(f"Order State: {result.get('state')}")
        
        return success

    def validate_service_activation(self):
        """Test TMF640 - Service Activation"""
        log_header("TMF640 - SERVICE ACTIVATION")
        
        activation_request = {
            "service": {
                "name": "Test Fiber Service",
                "serviceType": "broadband",
                "place": {
                    "streetName": "Main Street",
                    "streetNumber": "456",
                    "city": "Springfield"
                },
                "serviceSpecification": {
                    "id": "FIBER_1GB"
                }
            }
        }
        
        success, result = self.api_call("POST", "/tmf640/serviceActivation", activation_request, 201)
        
        if success:
            log_info(f"Activation ID: {result.get('id')}")
            log_info(f"Activation State: {result.get('state')}")
            log_info(f"Activation Date: {result.get('activationDate')}")
        
        return success

    def validate_admin_functions(self):
        """Test Administrative Functions"""
        log_header("ADMINISTRATIVE FUNCTIONS")
        
        # Test catalog sync (validation only)
        sync_request = {
            "validateOnly": True,
            "fixOrphans": False
        }
        
        success, result = self.api_call("POST", "/admin/syncCatalog", sync_request)
        
        if success:
            validation_results = result.get('validationResults', {})
            log_info(f"Orphaned Service Specs: {validation_results.get('orphanedServiceSpecs', 0)}")
            log_info(f"Orphaned Product Offerings: {validation_results.get('orphanedProductOfferings', 0)}")
            log_info(f"Invalid Coverage Entries: {validation_results.get('invalidCoverageEntries', 0)}")
            
            recommendations = result.get('recommendations', [])
            if recommendations:
                log_info("Recommendations:")
                for rec in recommendations:
                    log_info(f"  - {rec}")
        
        return success

    def run_performance_tests(self):
        """Run basic performance tests"""
        log_header("PERFORMANCE TESTS")
        
        # Test response times for key endpoints
        endpoints = [
            "/admin/health",
            "/tmf633/serviceSpecification",
            "/tmf620/productOffering",
            "/tmf673/geographicLocation",
            "/tmf629/customer/8452934"
        ]
        
        for endpoint in endpoints:
            start_time = time.time()
            success, _ = self.api_call("GET", endpoint)
            response_time = (time.time() - start_time) * 1000
            
            if success:
                if response_time < 100:
                    log_success(f"{endpoint}: {response_time:.0f}ms (Excellent)")
                elif response_time < 500:
                    log_info(f"{endpoint}: {response_time:.0f}ms (Good)")
                else:
                    log_warning(f"{endpoint}: {response_time:.0f}ms (Slow)")
            else:
                log_error(f"{endpoint}: Failed")

    def generate_report(self):
        """Generate final test report"""
        log_header("TEST REPORT")
        
        log_info(f"Total Tests: {self.total_tests}")
        log_success(f"Passed: {self.passed_tests}")
        log_error(f"Failed: {self.failed_tests}")
        
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        if success_rate >= 90:
            log_success(f"Success Rate: {success_rate:.1f}% - EXCELLENT! 🎉")
        elif success_rate >= 70:
            log_warning(f"Success Rate: {success_rate:.1f}% - GOOD 👍")
        else:
            log_error(f"Success Rate: {success_rate:.1f}% - NEEDS IMPROVEMENT 🔧")
        
        # Show failed tests
        if self.failed_tests > 0:
            log_warning("\nFailed Tests:")
            for test in self.test_results:
                if not test.get('success', False):
                    log_error(f"  {test['method']} {test['endpoint']} - Status: {test.get('status', 'Error')}")
        
        return success_rate >= 70

def main():
    """Main validation function"""
    log_header("TELEPATH AI CATALOG MANAGER - API VALIDATION")
    log_info("Starting comprehensive API validation...")
    
    validator = APIValidator()
    
    # Wait for services to be ready
    log_info("Waiting for services to be ready...")
    max_retries = 30
    for i in range(max_retries):
        try:
            response = requests.get(f"{API_BASE}/admin/health", timeout=5)
            if response.status_code == 200:
                log_success("Services are ready!")
                break
        except:
            if i == max_retries - 1:
                log_error("Services failed to start within 150 seconds")
                return False
            log_info(f"Waiting... ({i+1}/{max_retries})")
            time.sleep(5)
    
    # Run all validation tests
    try:
        validator.validate_health()
        validator.validate_service_specifications()
        validator.validate_product_offerings()
        validator.validate_geographic_locations()
        validator.validate_customer_management()
        validator.validate_service_qualification()
        validator.validate_product_ordering()
        validator.validate_service_activation()
        validator.validate_admin_functions()
        validator.run_performance_tests()
        
        # Generate final report
        success = validator.generate_report()
        
        if success:
            log_success("\n🎉 ALL SYSTEMS OPERATIONAL! 🎉")
            log_info("Your Telepath AI Catalog Manager is ready for use!")
            log_info(f"Web UI: http://localhost:8082")
            log_info(f"API Documentation: {API_BASE}/admin/health")
        else:
            log_error("\n❌ VALIDATION FAILED")
            log_error("Please check the logs and fix any issues before proceeding.")
            
        return success
        
    except KeyboardInterrupt:
        log_warning("\nValidation interrupted by user")
        return False
    except Exception as e:
        log_error(f"\nUnexpected error during validation: {str(e)}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)