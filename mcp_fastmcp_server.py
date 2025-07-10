    await ensure_session()
    
    url = f"{CATALOG_MANAGER_URL}/api/orders/recent"
    async with session.get(url, timeout=DEFAULT_TIMEOUT) as response:
        orders = await response.json()
        return json.dumps(orders, indent=2)

# Tools for performing actions

@mcp.tool()
async def service_qualification(
    address: Dict[str, str],
    serviceSpecification: Dict[str, str]
) -> Dict[str, Any]:
    """Check if a service is available at a specific location (TMF637)
    
    Args:
        address: Address with streetName, streetNumber, and city
        serviceSpecification: Service specification with id and name
    
    Returns:
        Service qualification result
    """
    await ensure_session()
    
    url = f"{CATALOG_MANAGER_URL}/tmf637/serviceQualification"
    request_data = {
        "address": address,
        "serviceSpecification": serviceSpecification
    }
    
    try:
        async with session.post(url, json=request_data, timeout=DEFAULT_TIMEOUT) as response:
            result = await response.json()
            log_audit("service_qualification", request_data, result)
            return result
    except Exception as e:
        error_result = {"error": str(e)}
        log_audit("service_qualification", request_data, error_result)
        raise Exception(f"Service qualification failed: {str(e)}")

@mcp.tool()
async def customer_management(customerId: str) -> Dict[str, Any]:
    """Get customer information including account status and eligibility (TMF629)
    
    Args:
        customerId: The customer ID to look up
    
    Returns:
        Customer information
    """
    await ensure_session()
    
    url = f"{CATALOG_MANAGER_URL}/tmf629/customer/{customerId}"
    
    try:
        async with session.get(url, timeout=DEFAULT_TIMEOUT) as response:
            result = await response.json()
            log_audit("customer_management", {"customerId": customerId}, result)
            return result
    except Exception as e:
        error_result = {"error": str(e)}
        log_audit("customer_management", {"customerId": customerId}, error_result)
        raise Exception(f"Customer lookup failed: {str(e)}")

@mcp.tool()
async def product_ordering(
    orderDate: str,
    externalId: str,
    customerId: str,
    productOfferingId: str,
    address: Dict[str, str]
) -> Dict[str, Any]:
    """Create a product order for a customer (TMF622)
    
    Args:
        orderDate: Order date
        externalId: External order ID
        customerId: Customer ID
        productOfferingId: Product offering ID
        address: Delivery address
    
    Returns:
        Created order information
    """
    await ensure_session()
    
    url = f"{CATALOG_MANAGER_URL}/tmf622/productOrder"
    
    # Transform to TMF622 format
    order_data = {
        "orderDate": orderDate,
        "externalId": externalId,
        "relatedParty": [{
            "id": customerId,
            "role": "customer"
        }],
        "orderItem": [{
            "action": "add",
            "productOffering": {
                "id": productOfferingId
            },
            "product": {
                "place": address
            }
        }]
    }
    
    try:
        async with session.post(url, json=order_data, timeout=DEFAULT_TIMEOUT) as response:
            result = await response.json()
            log_audit("product_ordering", order_data, result)
            return result
    except Exception as e:
        error_result = {"error": str(e)}
        log_audit("product_ordering", order_data, error_result)
        raise Exception(f"Product ordering failed: {str(e)}")

@mcp.tool()
async def service_activation(
    serviceName: str,
    serviceType: str,
    address: Dict[str, str],
    serviceSpecificationId: str
) -> Dict[str, Any]:
    """Activate a service in the network (TMF640)
    
    Args:
        serviceName: Service name
        serviceType: Service type (e.g., "Broadband")
        address: Service address
        serviceSpecificationId: Service specification ID
    
    Returns:
        Service activation result
    """
    await ensure_session()
    
    url = f"{CATALOG_MANAGER_URL}/tmf640/serviceActivation"
    
    # Transform to TMF640 format
    activation_data = {
        "service": {
            "name": serviceName,
            "serviceType": serviceType,
            "place": address,
            "serviceSpecification": {
                "id": serviceSpecificationId
            }
        }
    }
    
    try:
        async with session.post(url, json=activation_data, timeout=DEFAULT_TIMEOUT) as response:
            result = await response.json()
            log_audit("service_activation", activation_data, result)
            return result
    except Exception as e:
        error_result = {"error": str(e)}
        log_audit("service_activation", activation_data, error_result)
        raise Exception(f"Service activation failed: {str(e)}")

# Fault Management Tools
@mcp.tool()
async def check_service_status(
    location: str
) -> Dict[str, Any]:
    """Check service status and alarms for a location (TMF656)
    
    Args:
        location: Street name or area to check
    
    Returns:
        Current alarms and service status
    """
    await ensure_session()
    
    url = f"{FAULT_MANAGER_URL}/tmf656/alarmManagement/alarms/{location}"
    
    try:
        async with session.get(url, timeout=DEFAULT_TIMEOUT) as response:
            alarms = await response.json()
            
        # Also get service impact
        impact_url = f"{FAULT_MANAGER_URL}/api/service-impact/{location}"
        async with session.get(impact_url, timeout=DEFAULT_TIMEOUT) as response:
            impact = await response.json()
            
        result = {
            "location": location,
            "alarms": alarms,
            "service_impact": impact
        }
        
        log_audit("check_service_status", {"location": location}, result)
        return result
    except Exception as e:
        error_result = {"error": str(e)}
        log_audit("check_service_status", {"location": location}, error_result)
        raise Exception(f"Service status check failed: {str(e)}")

@mcp.tool()
async def create_trouble_ticket(
    customerId: str,
    description: str,
    severity: str = "medium",
    relatedAlarmId: str = None
) -> Dict[str, Any]:
    """Create a trouble ticket for customer issue (TMF621)
    
    Args:
        customerId: Customer reporting the issue
        description: Description of the problem
        severity: Severity level (low, medium, high, critical)
        relatedAlarmId: Optional related network alarm ID
    
    Returns:
        Created trouble ticket
    """
    await ensure_session()
    
    url = f"{FAULT_MANAGER_URL}/tmf621/troubleTicket"
    
    ticket_data = {
        "customerId": customerId,
        "description": description,
        "severity": severity,
        "relatedAlarmId": relatedAlarmId
    }
    
    try:
        async with session.post(url, json=ticket_data, timeout=DEFAULT_TIMEOUT) as response:
            result = await response.json()
            log_audit("create_trouble_ticket", ticket_data, result)
            return result
    except Exception as e:
        error_result = {"error": str(e)}
        log_audit("create_trouble_ticket", ticket_data, error_result)
        raise Exception(f"Trouble ticket creation failed: {str(e)}")

@mcp.tool()
async def get_remediation_recommendations(
    alarmType: str,
    severity: str
) -> Dict[str, Any]:
    """Get recommended remediation actions for an alarm
    
    Args:
        alarmType: Type of alarm (fiber_cut, power_outage, equipment_failure)
        severity: Severity of the issue
    
    Returns:
        Recommended actions and estimated repair time
    """
    await ensure_session()
    
    url = f"{FAULT_MANAGER_URL}/api/remediation/recommend"
    
    request_data = {
        "alarmType": alarmType,
        "severity": severity
    }
    
    try:
        async with session.post(url, json=request_data, timeout=DEFAULT_TIMEOUT) as response:
            result = await response.json()
            log_audit("get_remediation_recommendations", request_data, result)
            return result
    except Exception as e:
        error_result = {"error": str(e)}
        log_audit("get_remediation_recommendations", request_data, error_result)
        raise Exception(f"Failed to get recommendations: {str(e)}")

@mcp.tool()
async def execute_remediation_action(
    alarmId: str,
    actionType: str
) -> Dict[str, Any]:
    """Execute a remediation action for an alarm
    
    Args:
        alarmId: ID of the alarm to remediate
        actionType: Type of action (acknowledge_alarm, dispatch_technician, notify_customers)
    
    Returns:
        Remediation action status
    """
    await ensure_session()
    
    url = f"{FAULT_MANAGER_URL}/api/remediation/execute"
    
    action_data = {
        "alarmId": alarmId,
        "actionType": actionType
    }
    
    try:
        async with session.post(url, json=action_data, timeout=DEFAULT_TIMEOUT) as response:
            result = await response.json()
            log_audit("execute_remediation_action", action_data, result)
            return result
    except Exception as e:
        error_result = {"error": str(e)}
        log_audit("execute_remediation_action", action_data, error_result)
        raise Exception(f"Remediation action failed: {str(e)}")

# Fault Management Resources
@mcp.resource("alarms://current")
async def get_current_alarms() -> str:
    """Get all current network alarms"""
    await ensure_session()
    
    url = f"{FAULT_MANAGER_URL}/tmf656/alarmManagement/alarms"
    async with session.get(url, timeout=DEFAULT_TIMEOUT) as response:
        alarms = await response.json()
        return json.dumps(alarms, indent=2)

@mcp.resource("alarms://location/{location}")
async def get_location_alarms(location: str) -> str:
    """Get alarms for a specific location"""
    await ensure_session()
    
    url = f"{FAULT_MANAGER_URL}/tmf656/alarmManagement/alarms/{location}"
    async with session.get(url, timeout=DEFAULT_TIMEOUT) as response:
        alarms = await response.json()
        return json.dumps(alarms, indent=2)

if __name__ == "__main__":
    print(f"Running Telepath MCP Server on {HOST}:{PORT}")
    print(f"Catalog Manager URL: {CATALOG_MANAGER_URL}")
    print(f"Fault Manager URL: {FAULT_MANAGER_URL}")
    try:
        mcp.run(transport="streamable-http")
    finally:
        # Cleanup session if exists
        if session:
            asyncio.run(cleanup_session())
