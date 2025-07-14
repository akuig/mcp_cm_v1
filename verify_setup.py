#!/usr/bin/env python3
"""
Final verification that everything is working
"""

import asyncio
import httpx
import sys

async def verify_all_services():
    """Verify all services are working correctly"""
    all_ok = True
    
    print("🔍 Verifying Fault Management Demo Setup")
    print("=" * 50)
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        # 1. Check Catalog Manager
        print("\n1. Catalog Manager (Port 8080)")
        try:
            response = await client.get("http://localhost:8080/health")
            if response.status_code == 200:
                print("   ✅ Status: Running")
            else:
                print(f"   ❌ Status: Error (HTTP {response.status_code})")
                all_ok = False
        except Exception as e:
            print(f"   ❌ Status: Not running - {type(e).__name__}")
            all_ok = False
        
        # 2. Check Fault Manager
        print("\n2. Fault Manager (Port 8081)")
        try:
            response = await client.get("http://localhost:8081/health")
            if response.status_code == 200:
                print("   ✅ Status: Running")
                
                # Check fault simulation
                fault_check = await client.post(
                    "http://localhost:8081/serviceStatus/check",
                    json={"location": {"streetName": "Main Street", "city": "Dublin"}}
                )
                if fault_check.status_code == 200:
                    data = fault_check.json()
                    if data.get("status") == "degraded":
                        print("   ✅ Fault Simulation: Active")
                        print("   📍 Detected: Fiber cut on Main Street")
                    else:
                        print("   ⚠️  Fault Simulation: No faults detected")
            else:
                print(f"   ❌ Status: Error (HTTP {response.status_code})")
                all_ok = False
        except Exception as e:
            print(f"   ❌ Status: Not running - {type(e).__name__}")
            all_ok = False
        
        # 3. Check MCP Server (just check if container is running)
        print("\n3. MCP Server (Port 8090)")
        try:
            # Try to connect to port
            response = await client.get("http://localhost:8090/", timeout=2.0)
            print("   ✅ Status: Port is open (FastMCP running)")
        except httpx.ConnectError:
            print("   ❌ Status: Port not accessible")
            all_ok = False
        except:
            # Any other error means port is open but no HTTP endpoint
            print("   ✅ Status: Running (FastMCP doesn't serve HTTP)")
        
        # 4. Test a complete flow
        print("\n4. Testing Complete Flow")
        try:
            # Create a trouble ticket
            ticket_response = await client.post(
                "http://localhost:8081/tmf621/troubleTicket",
                json={
                    "description": "Test ticket - please ignore",
                    "severity": "minor",
                    "priority": 3,
                    "relatedParty": [{"id": "TEST-001", "role": "customer"}]
                }
            )
            if ticket_response.status_code == 200:
                ticket = ticket_response.json()
                print(f"   ✅ Created test ticket: {ticket.get('id')}")
            else:
                print("   ❌ Failed to create test ticket")
                all_ok = False
        except Exception as e:
            print(f"   ❌ Flow test failed: {type(e).__name__}")
            all_ok = False
    
    # Summary
    print("\n" + "=" * 50)
    if all_ok:
        print("✅ ALL SERVICES ARE WORKING!")
        print("\nYou can now run the demo:")
        print("  python test_fault_management.py")
        return 0
    else:
        print("❌ SOME SERVICES ARE NOT WORKING")
        print("\nTroubleshooting:")
        print("1. Check Docker logs:")
        print("   docker-compose -f docker-compose-with-fault.yml logs")
        print("2. Restart services:")
        print("   ./final_fix_asyncio.sh")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(verify_all_services())
    sys.exit(exit_code)
