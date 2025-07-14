#!/usr/bin/env python3
"""
Test script for Fault Management scenario
Demonstrates the complete flow from fault detection to resolution

Note: This test script calls the Fault Manager APIs directly for demonstration.
In production, these would be called through the MCP server by Claude.
"""

import asyncio
import json
import httpx
from datetime import datetime
from typing import Dict

# Configuration
MCP_SERVER_URL = "http://localhost:8090"
FAULT_MANAGER_URL = "http://localhost:8081"

# Test data
JANE_DOE_CUSTOMER_ID = "CUST-001"
JANE_DOE_ADDRESS = {
    "streetName": "Main Street",
    "streetNumber": "123",
    "city": "Dublin"
}
JANE_DOE_SERVICE_ID = "SVC-JANE-001"

class FaultManagementDemo:
    def __init__(self):
        self.client = httpx.AsyncClient()
    
    async def call_service_api(self, endpoint: str, method: str = "POST", data: Dict = None) -> Dict:
        """Call service APIs directly"""
        if method == "POST":
            response = await self.client.post(endpoint, json=data)
        else:
            response = await self.client.get(endpoint)
        return response.json()
    
    async def simulate_customer_call(self):
        """Simulate Jane Doe calling about service issue"""
        print("\n" + "="*60)
        print("FAULT MANAGEMENT DEMO - Jane Doe Service Issue")
        print("="*60)
        
        print("\n📞 Customer Call at 10:15 AM")
        print("Customer: 'Hi, I'm Jane Doe at 123 Main Street. My internet just went down!'")
        
        # Step 1: Check service status
        print("\n🔍 Agent: 'Let me check the service status for your location...'")
        status_result = await self.call_service_api(
            f"{FAULT_MANAGER_URL}/serviceStatus/check",
            data={
                "location": JANE_DOE_ADDRESS,
                "serviceId": JANE_DOE_SERVICE_ID
            }
        )
        
        print(f"\nService Status Result:")
        print(json.dumps(status_result, indent=2))
        
        if status_result.get("status") == "degraded":
            print("\n⚠️  Agent: 'I've identified the issue. There's a fiber cut on Main Street.'")
            
            # Get fault details
            faults = status_result.get("networkFaults", [])
            if faults:
                fault = faults[0]
                print(f"\nFault Details:")
                print(f"- Type: {fault['type']}")
                print(f"- Description: {fault['description']}")
                print(f"- Severity: {fault['severity']}")
                print(f"- Estimated Resolution: {fault['estimatedResolution']}")
            
            # Show recommended actions
            print("\n💡 Recommended Actions:")
            for action in status_result.get("recommendedActions", []):
                print(f"- {action['action']}: {action['description']}")
                print(f"  Priority: {action['priority']}, Duration: {action['estimatedDuration']}")
        
        return status_result
    
    async def execute_recovery_actions(self, fault_id: str):
        """Execute the recommended recovery actions"""
        print("\n" + "-"*60)
        print("EXECUTING RECOVERY ACTIONS")
        print("-"*60)
        
        # Step 1: Reroute traffic for immediate relief
        print("\n🔄 Step 1: Rerouting traffic through backup path...")
        reroute_result = await self.call_service_api(
            f"{FAULT_MANAGER_URL}/serviceStatus/executeAction",
            data={
                "action": "REROUTE_TRAFFIC",
                "faultId": fault_id
            }
        )
        
        if reroute_result.get("status") == "success":
            result = reroute_result["result"]
            print(f"✅ {result['message']}")
            print(f"   - Services restored: {result['affectedServices']}")
            print(f"   - Restoration time: {result['estimatedRestoration']}")
            print(f"   - Backup path load: {result['backupPathUtilization']}")
        
        # Step 2: Create trouble ticket
        print("\n📝 Step 2: Creating trouble ticket...")
        ticket_result = await self.call_service_api(
            f"{FAULT_MANAGER_URL}/tmf621/troubleTicket",
            data={
                "description": "No internet service - fiber cut on Main Street",
                "severity": "major",
                "priority": 1,
                "relatedParty": [{
                    "id": JANE_DOE_CUSTOMER_ID,
                    "role": "customer",
                    "name": f"Customer {JANE_DOE_CUSTOMER_ID}"
                }],
                "serviceId": JANE_DOE_SERVICE_ID,
                "note": [{
                    "text": "Contact phone: +353 1 234 5678",
                    "date": datetime.utcnow().isoformat()
                }]
            }
        )
        
        print(f"✅ Trouble ticket created: {ticket_result.get('id')}")
        print(f"   State: {ticket_result.get('state')}")
        
        # Step 3: Dispatch technician
        print("\n👷 Step 3: Dispatching field technician...")
        dispatch_result = await self.call_service_api(
            f"{FAULT_MANAGER_URL}/serviceStatus/executeAction",
            data={
                "action": "DISPATCH_TECHNICIAN",
                "faultId": fault_id
            }
        )
        
        if dispatch_result.get("status") == "success":
            result = dispatch_result["result"]
            print(f"✅ {result['message']}")
            print(f"   - Technician: {result['technician']}")
            print(f"   - ETA: {result['estimatedArrival']}")
            print(f"   - Repair time: {result['estimatedRepairTime']}")
        
        # Step 4: Notify customers
        print("\n📱 Step 4: Notifying affected customers...")
        notify_result = await self.call_service_api(
            f"{FAULT_MANAGER_URL}/serviceStatus/executeAction",
            data={
                "action": "NOTIFY_CUSTOMERS",
                "faultId": fault_id
            }
        )
        
        if notify_result.get("status") == "success":
            result = notify_result["result"]
            print(f"✅ {result['message']}")
            print(f"   - Notifications sent: {result['notificationsSent']}")
            print(f"   - Method: {result['method']}")
        
        return ticket_result.get("id")
    
    async def check_area_problems(self):
        """Check all service problems in the area"""
        print("\n" + "-"*60)
        print("CHECKING AREA-WIDE SERVICE PROBLEMS")
        print("-"*60)
        
        problems_result = await self.call_service_api(
            f"{FAULT_MANAGER_URL}/tmf656/serviceProblem?location=Main%20Street&state=inProgress",
            method="GET"
        )
        
        print(f"\nActive service problems on Main Street: {len(problems_result)}")
        for problem in problems_result[:3]:  # Show first 3
            print(f"\n- Problem ID: {problem['id']}")
            print(f"  Description: {problem['description']}")
            print(f"  Severity: {problem['severity']}")
            print(f"  Affected services: {len(problem.get('affectedServices', []))}")
    
    async def simulate_resolution(self, fault_id: str):
        """Simulate fault resolution"""
        print("\n" + "-"*60)
        print("FAULT RESOLUTION (Simulated at 2:00 PM)")
        print("-"*60)
        
        # Mark fault as resolved
        response = await self.client.post(
            f"{FAULT_MANAGER_URL}/fault/resolve/{fault_id}"
        )
        
        if response.status_code == 200:
            print(f"✅ Fault {fault_id} marked as resolved")
            
            # Check service status again
            print("\n🔍 Checking service status after resolution...")
            status_result = await self.call_service_api(
                f"{FAULT_MANAGER_URL}/serviceStatus/check",
                data={"location": JANE_DOE_ADDRESS}
            )
            
            print(f"Service Status: {status_result.get('status')}")
            if status_result.get('status') == 'operational':
                print("✅ All services restored to normal operation!")
    
    async def run_demo(self):
        """Run the complete fault management demo"""
        try:
            # 1. Customer reports issue
            status = await self.simulate_customer_call()
            
            # 2. Execute recovery actions if there's a fault
            if status.get("networkFaults"):
                fault_id = status["networkFaults"][0]["id"]
                ticket_id = await self.execute_recovery_actions(fault_id)
                
                # 3. Check area-wide problems
                await self.check_area_problems()
                
                # 4. Simulate resolution
                await asyncio.sleep(2)  # Wait a bit
                await self.simulate_resolution(fault_id)
            
            print("\n" + "="*60)
            print("DEMO COMPLETED SUCCESSFULLY")
            print("="*60)
            
        finally:
            await self.client.aclose()

async def check_service_health():
    """Check if required services are healthy"""
    async with httpx.AsyncClient() as client:
        services_ok = True
        
        # Check Fault Manager
        try:
            response = await client.get("http://localhost:8081/docs", timeout=5.0)
            if response.status_code != 200:
                print(f"❌ Fault Manager not ready (status: {response.status_code})")
                services_ok = False
        except Exception as e:
            print(f"❌ Fault Manager not responding: {type(e).__name__}")
            services_ok = False
        
        # Check Catalog Manager
        try:
            response = await client.get("http://localhost:8080/health", timeout=5.0)
            if response.status_code != 200:
                print(f"❌ Catalog Manager not ready (status: {response.status_code})")
                services_ok = False
        except Exception as e:
            print(f"❌ Catalog Manager not responding: {type(e).__name__}")
            services_ok = False
            
        return services_ok

async def main():
    """Main entry point"""
    # Check services first
    print("Checking if services are running...")
    services_ok = await check_service_health()
    
    if not services_ok:
        print("\n⚠️  Required services are not running!")
        print("\nPlease start services with:")
        print("  docker-compose -f docker-compose-with-fault.yml up -d")
        print("\nThen wait 15-20 seconds for services to initialize.")
        return
    
    print("✅ All services are running!\n")
    
    # Run the demo
    demo = FaultManagementDemo()
    await demo.run_demo()

if __name__ == "__main__":
    print("Starting Fault Management Demo...")
    print("Make sure all services are running:")
    print("- Catalog Manager (port 8080)")
    print("- Fault Manager (port 8081)")
    print("- MCP Server (port 8090)")
    print()
    
    asyncio.run(main())
