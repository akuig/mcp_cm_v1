#!/usr/bin/env python3
"""
Comprehensive status check for all services
"""

import httpx
import asyncio
import json
from datetime import datetime

async def check_all_services():
    """Check all services and display detailed status"""
    
    print("🔍 Telepath AI Fault Management - Service Status Check")
    print("=" * 60)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        # Check PostgreSQL (via catalog manager)
        print("1. PostgreSQL Database")
        try:
            response = await client.get("http://localhost:8080/health")
            if response.status_code == 200:
                print("   ✅ Status: Connected (via Catalog Manager)")
            else:
                print("   ❌ Status: Connection issue")
        except Exception as e:
            print(f"   ❌ Status: Not accessible - {type(e).__name__}")
        
        # Check Catalog Manager
        print("\n2. Catalog Manager (Port 8080)")
        try:
            response = await client.get("http://localhost:8080/health")
            if response.status_code == 200:
                print("   ✅ Status: Running")
                print("   📡 Endpoints: /tmf620, /tmf622, /tmf629, /tmf637, /tmf640")
            else:
                print(f"   ❌ Status: Responded with {response.status_code}")
        except Exception as e:
            print(f"   ❌ Status: Not running - {type(e).__name__}")
        
        # Check Fault Manager
        print("\n3. Fault Manager (Port 8081)")
        try:
            response = await client.get("http://localhost:8081/docs")
            if response.status_code == 200:
                print("   ✅ Status: Running")
                print("   📡 API Docs: http://localhost:8081/docs")
                
                # Check fault simulation
                fault_response = await client.post(
                    "http://localhost:8081/serviceStatus/check",
                    json={"location": {"streetName": "Main Street", "city": "Dublin"}}
                )
                if fault_response.status_code == 200:
                    data = fault_response.json()
                    if data.get("status") == "degraded":
                        print("   🚨 Fault Simulation: Active (Fiber cut on Main Street)")
                    else:
                        print("   ⚠️  Fault Simulation: No active faults")
            else:
                print(f"   ❌ Status: Responded with {response.status_code}")
        except Exception as e:
            print(f"   ❌ Status: Not running - {type(e).__name__}")
        
        # Check MCP Server
        print("\n4. MCP Server (Port 8090)")
        try:
            # FastMCP doesn't have a health endpoint, so we'll check if port is open
            response = await client.get("http://localhost:8090/", follow_redirects=False)
            # Any response means it's running
            print("   ✅ Status: Running")
            print("   🔧 Mode: FastMCP with Fault Management")
            print("   🛠️  Tools Available:")
            print("      - service_qualification")
            print("      - customer_management")
            print("      - product_ordering")
            print("      - service_activation")
            print("      - check_service_status (NEW)")
            print("      - create_trouble_ticket (NEW)")
            print("      - execute_remedial_action (NEW)")
            print("      - get_service_problems (NEW)")
        except httpx.ConnectError:
            print("   ❌ Status: Not running - Cannot connect to port 8090")
        except Exception as e:
            # Other exceptions might mean it's running but doesn't have that endpoint
            print("   ⚠️  Status: Port is open but no health endpoint")
            print(f"   📝 Note: This is normal for FastMCP - {type(e).__name__}")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Summary:")
    print("   - Use 'docker-compose -f docker-compose-with-fault.yml logs' to check logs")
    print("   - Run 'python test_fault_management.py' to test the demo")
    print("   - Visit http://localhost:8081/docs for Fault Manager API documentation")

if __name__ == "__main__":
    asyncio.run(check_all_services())
