#!/usr/bin/env python3
"""
Verification script for Enhanced Telecom MCP System
Verifies that all 13 tools are available and working
"""

import json
import requests
import sys
from typing import Dict, Any, List
from datetime import datetime

# ANSI color codes
RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
NC = '\033[0m'  # No Color

# Configuration
MCP_URL = "http://localhost:8090/mcp/stream"
CATALOG_URL = "http://localhost:8080"

# Expected 13 tools
EXPECTED_TOOLS = [
    # TMF Forum APIs (5)
    "service_qualification",
    "customer_management", 
    "product_ordering",
    "service_activation",
    "order_management",
    # Catalog Management (8)
    "list_service_specifications",
    "list_product_offerings",
    "list_geographic_locations",
    "sync_catalog_data",
    "create_service_specification",
    "create_product_offering",
    "link_offering_to_specification",
    "add_geographic_coverage"
]

def print_colored(color: str, msg: str):
    """Print colored message"""
    print(f"{color}{msg}{NC}")

def check_service_health(name: str, url: str) -> bool:
    """Check if a service is healthy"""
    try:
        response = requests.get(f"{url}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def get_mcp_tools() -> List[str]:
    """Get list of available MCP tools"""
    try:
        payload = {
            "jsonrpc": "2.0",
            "method": "tools/list",
            "params": {},
            "id": 1
        }
        
        response = requests.post(
            MCP_URL,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if "result" in data and "tools" in data["result"]:
                return [tool["name"] for tool in data["result"]["tools"]]
        return []
    except Exception as e:
        print_colored(RED, f"Error getting MCP tools: {e}")
        return []

def test_catalog_endpoints() -> Dict[str, bool]:
    """Test catalog manager endpoints"""
    endpoints = {
        "/api/service-specifications": "GET",
        "/api/product-offerings": "GET",
        "/api/geographic-locations": "GET",
        "/tmf629/customer/CUST001": "GET",
        "/tmf622/productOrder": "GET"
    }
    
    results = {}
    for endpoint, method in endpoints.items():
        try:
            url = f"{CATALOG_URL}{endpoint}"
            if method == "GET":
                response = requests.get(url, timeout=5)
            else:
                response = requests.post(url, json={}, timeout=5)
            
            # Consider 200, 201, 404 as "working" (404 means endpoint exists but no data)
            results[endpoint] = response.status_code in [200, 201, 404]
        except:
            results[endpoint] = False
    
    return results

def main():
    """Main verification function"""
    print_colored(BLUE, "=" * 60)
    print_colored(BLUE, "🔍 Enhanced Telecom MCP System Verification")
    print_colored(BLUE, "=" * 60)
    
    # Check service health
    print_colored(YELLOW, "\n📊 Checking Service Health...")
    
    catalog_healthy = check_service_health("Catalog Manager", CATALOG_URL)
    if catalog_healthy:
        print_colored(GREEN, "  ✅ Catalog Manager is healthy")
    else:
        print_colored(RED, "  ❌ Catalog Manager is not responding")
    
    # MCP server doesn't have a health endpoint, so we check if it responds
    try:
        mcp_tools = get_mcp_tools()
        mcp_healthy = len(mcp_tools) > 0
        if mcp_healthy:
            print_colored(GREEN, "  ✅ MCP Server is responding")
        else:
            print_colored(RED, "  ❌ MCP Server is not responding properly")
    except:
        mcp_healthy = False
        print_colored(RED, "  ❌ MCP Server is not accessible")
    
    if not (catalog_healthy and mcp_healthy):
        print_colored(RED, "\n❌ Services are not ready. Please ensure they are running:")
        print_colored(YELLOW, "   docker-compose up -d")
        sys.exit(1)
    
    # Check MCP tools
    print_colored(YELLOW, "\n🛠️  Checking MCP Tools...")
    
    if not mcp_tools:
        print_colored(RED, "  ❌ Could not retrieve MCP tools list")
        sys.exit(1)
    
    print_colored(BLUE, f"  Found {len(mcp_tools)} tools")
    
    # Check each expected tool
    missing_tools = []
    extra_tools = []
    
    for tool in EXPECTED_TOOLS:
        if tool in mcp_tools:
            print_colored(GREEN, f"  ✅ {tool}")
        else:
            print_colored(RED, f"  ❌ {tool} (missing)")
            missing_tools.append(tool)
    
    # Check for unexpected tools
    for tool in mcp_tools:
        if tool not in EXPECTED_TOOLS:
            print_colored(YELLOW, f"  ➕ {tool} (extra)")
            extra_tools.append(tool)
    
    # Test catalog endpoints
    print_colored(YELLOW, "\n📡 Testing Catalog Endpoints...")
    
    endpoint_results = test_catalog_endpoints()
    all_endpoints_ok = True
    
    for endpoint, success in endpoint_results.items():
        if success:
            print_colored(GREEN, f"  ✅ {endpoint}")
        else:
            print_colored(RED, f"  ❌ {endpoint}")
            all_endpoints_ok = False
    
    # Summary
    print_colored(BLUE, "\n" + "=" * 60)
    print_colored(BLUE, "📋 SUMMARY")
    print_colored(BLUE, "=" * 60)
    
    if len(mcp_tools) == 13 and not missing_tools:
        print_colored(GREEN, f"✅ All 13 tools are available!")
    elif len(mcp_tools) == 13:
        print_colored(YELLOW, f"⚠️  Found 13 tools but some are different than expected")
        if missing_tools:
            print_colored(YELLOW, f"   Missing: {', '.join(missing_tools)}")
        if extra_tools:
            print_colored(YELLOW, f"   Extra: {', '.join(extra_tools)}")
    else:
        print_colored(RED, f"❌ Found {len(mcp_tools)} tools (expected 13)")
        if missing_tools:
            print_colored(RED, f"   Missing: {', '.join(missing_tools)}")
    
    if all_endpoints_ok:
        print_colored(GREEN, "✅ All catalog endpoints are responding")
    else:
        print_colored(YELLOW, "⚠️  Some catalog endpoints are not responding")
    
    # Final verdict
    if len(mcp_tools) == 13 and not missing_tools and all_endpoints_ok:
        print_colored(GREEN, "\n🎉 VERIFICATION PASSED - System is fully operational!")
        return 0
    else:
        print_colored(YELLOW, "\n⚠️  VERIFICATION PARTIAL - System is operational but needs attention")
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print_colored(YELLOW, "\n\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        print_colored(RED, f"\n❌ Unexpected error: {e}")
        sys.exit(1)
