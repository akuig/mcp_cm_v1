#!/usr/bin/env python3
"""
Diagnostic script to check if all services are running
"""

import httpx
import asyncio
import sys

async def check_services():
    """Check if all required services are running"""
    services_ok = True
    
    async with httpx.AsyncClient() as client:
        # Check Catalog Manager
        try:
            response = await client.get("http://localhost:8080/health", timeout=5.0)
            if response.status_code == 200:
                print("✓ Catalog Manager (8080): Running")
            else:
                print(f"✗ Catalog Manager (8080): Responded with status {response.status_code}")
                services_ok = False
        except Exception as e:
            print(f"✗ Catalog Manager (8080): Not responding - {type(e).__name__}")
            services_ok = False
        
        # Check Fault Manager
        try:
            response = await client.get("http://localhost:8081/docs", timeout=5.0)
            if response.status_code == 200:
                print("✓ Fault Manager (8081): Running")
            else:
                print(f"✗ Fault Manager (8081): Responded with status {response.status_code}")
                services_ok = False
        except Exception as e:
            print(f"✗ Fault Manager (8081): Not responding - {type(e).__name__}")
            services_ok = False
        
        # Check MCP Server
        try:
            response = await client.get("http://localhost:8090/health", timeout=5.0)
            if response.status_code == 200:
                print("✓ MCP Server (8090): Running")
            else:
                print(f"✗ MCP Server (8090): Responded with status {response.status_code}")
                services_ok = False
        except Exception as e:
            print(f"✗ MCP Server (8090): Not responding - {type(e).__name__}")
            services_ok = False
        
        # Test Fault Manager functionality
        if services_ok:
            print("\nTesting Fault Manager functionality...")
            try:
                response = await client.post(
                    "http://localhost:8081/serviceStatus/check",
                    json={"location": {"streetName": "Main Street", "city": "Dublin"}}
                )
                if response.status_code == 200:
                    data = response.json()
                    if data.get("status") == "degraded":
                        print("✓ Fault simulation active: Fiber cut detected on Main Street")
                    else:
                        print("⚠ Fault simulation may not be active")
                else:
                    print(f"✗ Fault Manager API error: Status {response.status_code}")
            except Exception as e:
                print(f"✗ Fault Manager API error: {type(e).__name__}: {e}")
    
    return services_ok

if __name__ == "__main__":
    print("Checking service status...\n")
    services_ok = asyncio.run(check_services())
    
    if not services_ok:
        print("\n⚠ Some services are not running!")
        print("\nTo start services with fault management:")
        print("  docker-compose -f docker-compose-with-fault.yml up -d")
        print("\nTo check logs:")
        print("  docker-compose -f docker-compose-with-fault.yml logs")
        sys.exit(1)
    else:
        print("\n✓ All services are running!")
        print("\nYou can now run the fault management demo:")
        print("  python test_fault_management.py")
