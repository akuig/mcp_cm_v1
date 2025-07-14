#!/usr/bin/env python3
"""
Fault Manager Service - Manages network faults, service problems, and trouble tickets
Implements TMF621 (Trouble Ticket) and TMF656 (Service Problem Management)
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from enum import Enum
import uuid
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import httpx

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Fault Manager", version="1.0.0")

class ProblemState(str, Enum):
    SUBMITTED = "submitted"
    ACKNOWLEDGED = "acknowledged"
    IN_PROGRESS = "inProgress"
    RESOLVED = "resolved"
    CLOSED = "closed"
    CANCELLED = "cancelled"

class SeverityLevel(str, Enum):
    CRITICAL = "critical"
    MAJOR = "major"
    MINOR = "minor"
    WARNING = "warning"
    INFORMATION = "information"

class FaultType(str, Enum):
    FIBER_CUT = "fiber_cut"
    POWER_OUTAGE = "power_outage"
    EQUIPMENT_FAILURE = "equipment_failure"
    CONFIGURATION_ERROR = "configuration_error"
    NETWORK_CONGESTION = "network_congestion"

# Data Models
class ServiceProblem(BaseModel):
    id: str
    href: str
    createdDate: datetime
    description: str
    priority: int
    severity: SeverityLevel
    state: ProblemState
    affectedLocation: Dict
    affectedServices: List[Dict]
    rootCauseResource: Optional[Dict] = None
    impactStartTime: datetime
    impactEndTime: Optional[datetime] = None
    estimatedResolutionTime: Optional[datetime] = None
    resolutionAction: Optional[str] = None
    
class TroubleTicket(BaseModel):
    id: str
    href: str
    createdDate: datetime
    description: str
    severity: SeverityLevel
    priority: int
    state: ProblemState
    relatedParty: List[Dict]
    relatedServiceProblem: Optional[List[Dict]] = None
    troubleTicketRelationship: Optional[List[Dict]] = None
    statusChange: List[Dict]
    note: List[Dict]

class NetworkFault(BaseModel):
    id: str
    faultType: FaultType
    location: Dict
    affectedArea: Dict
    startTime: datetime
    endTime: Optional[datetime] = None
    impactedServices: List[str]
    severity: SeverityLevel
    description: str

# In-memory storage (would be database in production)
service_problems: Dict[str, ServiceProblem] = {}
trouble_tickets: Dict[str, TroubleTicket] = {}
network_faults: Dict[str, NetworkFault] = {}
service_to_location: Dict[str, Dict] = {}  # Maps service IDs to locations

# Initialize with a simulated fiber cut on Main Street
def initialize_fault_scenario():
    """Create initial fiber cut scenario on Main Street"""
    fault_id = str(uuid.uuid4())
    fault = NetworkFault(
        id=fault_id,
        faultType=FaultType.FIBER_CUT,
        location={
            "streetName": "Main Street",
            "city": "Dublin"
        },
        affectedArea={
            "streets": ["Main Street", "Oak Avenue", "First Street"],
            "postalCodes": ["D01", "D02"],
            "estimatedCustomersAffected": 150
        },
        startTime=datetime.utcnow(),
        impactedServices=[],  # Will be populated as services are checked
        severity=SeverityLevel.MAJOR,
        description="Fiber optic cable cut due to construction work on Main Street"
    )
    network_faults[fault_id] = fault
    logger.info(f"Initialized fault scenario: Fiber cut on Main Street")

# API Endpoints

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

@app.on_event("startup")
async def startup_event():
    """Initialize fault scenario on startup"""
    initialize_fault_scenario()

@app.post("/tmf656/serviceProblem", response_model=ServiceProblem)
async def create_service_problem(problem_data: Dict):
    """Create a new service problem"""
    problem_id = str(uuid.uuid4())
    problem = ServiceProblem(
        id=problem_id,
        href=f"/tmf656/serviceProblem/{problem_id}",
        createdDate=datetime.utcnow(),
        description=problem_data.get("description"),
        priority=problem_data.get("priority", 3),
        severity=problem_data.get("severity", SeverityLevel.MINOR),
        state=ProblemState.SUBMITTED,
        affectedLocation=problem_data.get("affectedLocation"),
        affectedServices=problem_data.get("affectedServices", []),
        impactStartTime=datetime.utcnow(),
        estimatedResolutionTime=datetime.utcnow() + timedelta(hours=2)
    )
    
    # Check if this problem is related to an existing network fault
    for fault in network_faults.values():
        if is_location_affected_by_fault(problem.affectedLocation, fault):
            problem.rootCauseResource = {
                "id": fault.id,
                "type": "NetworkFault",
                "description": fault.description
            }
            problem.severity = fault.severity
            break
    
    service_problems[problem_id] = problem
    return problem

@app.get("/tmf656/serviceProblem", response_model=List[ServiceProblem])
async def list_service_problems(
    state: Optional[ProblemState] = None,
    severity: Optional[SeverityLevel] = None,
    location: Optional[str] = None
):
    """List service problems with optional filters"""
    problems = list(service_problems.values())
    
    if state:
        problems = [p for p in problems if p.state == state]
    if severity:
        problems = [p for p in problems if p.severity == severity]
    if location:
        problems = [p for p in problems if location in str(p.affectedLocation)]
    
    return problems

@app.get("/tmf656/serviceProblem/{problem_id}", response_model=ServiceProblem)
async def get_service_problem(problem_id: str):
    """Get a specific service problem"""
    if problem_id not in service_problems:
        raise HTTPException(status_code=404, detail="Service problem not found")
    return service_problems[problem_id]

@app.post("/tmf621/troubleTicket", response_model=TroubleTicket)
async def create_trouble_ticket(ticket_data: Dict):
    """Create a new trouble ticket"""
    ticket_id = str(uuid.uuid4())
    ticket = TroubleTicket(
        id=ticket_id,
        href=f"/tmf621/troubleTicket/{ticket_id}",
        createdDate=datetime.utcnow(),
        description=ticket_data.get("description"),
        severity=ticket_data.get("severity", SeverityLevel.MINOR),
        priority=ticket_data.get("priority", 3),
        state=ProblemState.SUBMITTED,
        relatedParty=ticket_data.get("relatedParty", []),
        statusChange=[{
            "state": ProblemState.SUBMITTED,
            "changeDate": datetime.utcnow().isoformat()
        }],
        note=ticket_data.get("note", [])
    )
    
    trouble_tickets[ticket_id] = ticket
    
    # Automatically create a service problem if location is affected
    if "serviceId" in ticket_data:
        await check_and_create_service_problem(ticket_data["serviceId"], ticket_id)
    
    return ticket

@app.get("/tmf621/troubleTicket/{ticket_id}", response_model=TroubleTicket)
async def get_trouble_ticket(ticket_id: str):
    """Get a specific trouble ticket"""
    if ticket_id not in trouble_tickets:
        raise HTTPException(status_code=404, detail="Trouble ticket not found")
    return trouble_tickets[ticket_id]

@app.post("/serviceStatus/check")
async def check_service_status(request: Dict):
    """Check service status for a specific location or service"""
    location = request.get("location")
    service_id = request.get("serviceId")
    
    response = {
        "status": "operational",
        "problems": [],
        "networkFaults": [],
        "recommendedActions": []
    }
    
    # Check for network faults affecting the location
    for fault in network_faults.values():
        if location and is_location_affected_by_fault(location, fault):
            response["status"] = "degraded"
            response["networkFaults"].append({
                "id": fault.id,
                "type": fault.faultType.value,
                "description": fault.description,
                "severity": fault.severity.value,
                "estimatedResolution": (fault.startTime + timedelta(hours=4)).isoformat()
            })
            
            # Add recommended actions based on fault type
            if fault.faultType == FaultType.FIBER_CUT:
                response["recommendedActions"].extend([
                    {
                        "action": "DISPATCH_TECHNICIAN",
                        "description": "Dispatch field technician to repair fiber cut",
                        "priority": "high",
                        "estimatedDuration": "4 hours"
                    },
                    {
                        "action": "REROUTE_TRAFFIC",
                        "description": "Temporarily reroute traffic through backup path",
                        "priority": "immediate",
                        "estimatedDuration": "15 minutes"
                    },
                    {
                        "action": "NOTIFY_CUSTOMERS",
                        "description": "Send SMS notifications to affected customers",
                        "priority": "high",
                        "estimatedDuration": "5 minutes"
                    }
                ])
    
    # Check for service problems
    for problem in service_problems.values():
        if problem.state not in [ProblemState.RESOLVED, ProblemState.CLOSED]:
            if (location and location in str(problem.affectedLocation)) or \
               (service_id and any(s.get("id") == service_id for s in problem.affectedServices)):
                response["status"] = "degraded"
                response["problems"].append({
                    "id": problem.id,
                    "description": problem.description,
                    "severity": problem.severity.value,
                    "state": problem.state.value
                })
    
    return response

@app.post("/serviceStatus/executeAction")
async def execute_remedial_action(request: Dict):
    """Execute a remedial action"""
    action = request.get("action")
    target_fault_id = request.get("faultId")
    
    if action == "REROUTE_TRAFFIC":
        # Simulate traffic rerouting
        return {
            "status": "success",
            "action": action,
            "result": {
                "message": "Traffic successfully rerouted through backup fiber path",
                "affectedServices": 150,
                "estimatedRestoration": "15 minutes",
                "backupPathUtilization": "78%"
            }
        }
    
    elif action == "DISPATCH_TECHNICIAN":
        # Simulate technician dispatch
        ticket_id = str(uuid.uuid4())
        return {
            "status": "success",
            "action": action,
            "result": {
                "message": "Field technician dispatched",
                "ticketId": ticket_id,
                "technician": "John Smith (ID: TECH-4521)",
                "estimatedArrival": (datetime.utcnow() + timedelta(minutes=45)).isoformat(),
                "estimatedRepairTime": "3-4 hours"
            }
        }
    
    elif action == "NOTIFY_CUSTOMERS":
        # Simulate customer notification
        return {
            "status": "success",
            "action": action,
            "result": {
                "message": "Customer notifications sent",
                "notificationsSent": 150,
                "method": "SMS",
                "content": "We're aware of a service disruption in your area. Our team is working to resolve it. Estimated restoration: 4 hours."
            }
        }
    
    else:
        raise HTTPException(status_code=400, detail=f"Unknown action: {action}")

@app.post("/fault/resolve/{fault_id}")
async def resolve_fault(fault_id: str):
    """Mark a fault as resolved"""
    if fault_id not in network_faults:
        raise HTTPException(status_code=404, detail="Fault not found")
    
    fault = network_faults[fault_id]
    fault.endTime = datetime.utcnow()
    
    # Update related service problems
    for problem in service_problems.values():
        if problem.rootCauseResource and problem.rootCauseResource.get("id") == fault_id:
            problem.state = ProblemState.RESOLVED
            problem.impactEndTime = datetime.utcnow()
            problem.resolutionAction = "Network fault resolved"
    
    return {"message": "Fault resolved", "faultId": fault_id}

# Helper functions
def is_location_affected_by_fault(location: Dict, fault: NetworkFault) -> bool:
    """Check if a location is affected by a network fault"""
    if not location:
        return False
    
    location_street = location.get("streetName", "").lower()
    location_city = location.get("city", "").lower()
    
    # Check if location matches fault location
    fault_street = fault.location.get("streetName", "").lower()
    fault_city = fault.location.get("city", "").lower()
    
    if location_street == fault_street and location_city == fault_city:
        return True
    
    # Check if location is in affected area
    affected_streets = [s.lower() for s in fault.affectedArea.get("streets", [])]
    if location_street in affected_streets:
        return True
    
    return False

async def check_and_create_service_problem(service_id: str, ticket_id: str):
    """Check if service is affected by network fault and create service problem"""
    # This would normally check service inventory for location
    # For demo, we'll assume services on Main Street are affected
    for fault in network_faults.values():
        if fault.location.get("streetName") == "Main Street":
            problem_data = {
                "description": f"Service degradation due to {fault.description}",
                "severity": fault.severity,
                "priority": 1,
                "affectedServices": [{"id": service_id, "type": "BroadbandService"}],
                "affectedLocation": fault.location
            }
            problem = await create_service_problem(problem_data)
            
            # Link trouble ticket to service problem
            trouble_tickets[ticket_id].relatedServiceProblem = [{
                "id": problem.id,
                "href": problem.href
            }]
            break

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8081)
