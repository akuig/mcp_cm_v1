# Test Scenarios for Telepath AI MCP Server

## Setup Instructions

1. Build and start the system:
```bash
make build
make up
```

2. Verify services are running:
```bash
make health
```

3. Connect MCP Inspector to the server:
```bash
# In one terminal, get the MCP server stdio interface
docker exec -it mcp_server python mcp_server.py

# In another terminal, run the inspector
npx @anthropic/mcp-inspector
```

## Test Scenarios

### Scenario 1: Complete Happy Path - Fiber 500 Order
This follows the worked example from the documentation.

**Step 1: Check Service Availability**
Tool: `service_qualification`
```json
{
  "address": {
    "streetName": "Main Street",
    "streetNumber": "123",
    "city": "Springfield"
  },
  "serviceSpecification": {
    "id": "fiber500",
    "name": "Fiber 500 Mbps Plan"
  }
}
```
Expected Result: Qualified (Main Street has fiber coverage)

**Step 2: Check Customer Eligibility**
Tool: `customer_management`
```json
{
  "customerId": "8452934"
}
```
Expected Result: Jane Doe, active account, credit score 720, no overdue payments

**Step 3: Create Order**
Tool: `product_ordering`
```json
{
  "orderDate": "2025-01-07",
  "externalId": "WEB-ORDER-839201",
  "customerId": "8452934",
  "productOfferingId": "fiber500",
  "address": {
    "streetName": "Main Street",
    "streetNumber": "123",
    "city": "Springfield"
  }
}
```
Expected Result: Order created successfully with new order ID

**Step 4: Activate Service**
Tool: `service_activation`
```json
{
  "serviceName": "Fiber Internet",
  "serviceType": "Broadband",
  "address": {
    "streetNumber": "123",
    "streetName": "Main Street",
    "city": "Springfield"
  },
  "serviceSpecificationId": "fiber500"
}
```
Expected Result: Service activated successfully

### Scenario 2: Service Not Available
Test qualification for an area without fiber coverage.

Tool: `service_qualification`
```json
{
  "address": {
    "streetName": "Cherry Lane",
    "streetNumber": "456",
    "city": "Shelbyville"
  },
  "serviceSpecification": {
    "id": "fiber1000",
    "name": "Fiber 1 Gbps Plan"
  }
}
```
Expected Result: Unqualified - Service not available at this location

### Scenario 3: Customer with Bad Credit
Check a customer with overdue payments.

Tool: `customer_management`
```json
{
  "customerId": "8452935"
}
```
Expected Result: John Smith, has overdue payments, credit score 650

### Scenario 4: Suspended Account
Check a customer with suspended account.

Tool: `customer_management`
```json
{
  "customerId": "8452937"
}
```
Expected Result: Bob Williams, account status "suspended"

### Scenario 5: Non-existent Customer
Test error handling for invalid customer.

Tool: `customer_management`
```json
{
  "customerId": "9999999"
}
```
Expected Result: Error - Customer not found

### Scenario 6: Complete Order for Different Service Types

**Cable Service Order:**
Tool: `service_qualification`
```json
{
  "address": {
    "streetName": "Elm Street",
    "streetNumber": "789",
    "city": "Springfield"
  },
  "serviceSpecification": {
    "id": "cable200",
    "name": "Cable 200 Mbps Plan"
  }
}
```

**DSL Service Order:**
Tool: `service_qualification`
```json
{
  "address": {
    "streetName": "Pine Road",
    "streetNumber": "321",
    "city": "Springfield"
  },
  "serviceSpecification": {
    "id": "dsl50",
    "name": "DSL 50 Mbps Plan"
  }
}
```

## Verification Commands

Check database state after tests:
```bash
# Connect to database
make db-shell

# Check customers
SELECT * FROM customers;

# Check service coverage
SELECT * FROM service_coverage;

# Check orders created
SELECT * FROM orders;

# Check activations
SELECT * FROM service_activations;

# Exit
\q
```

## Error Scenarios to Test

1. **Missing Required Fields**: Try calling tools without required parameters
2. **Invalid Data Types**: Send strings where numbers are expected
3. **Network Timeout**: Stop the catalog-manager container and try calling tools
4. **Database Connection Loss**: Stop the postgres container and try operations

## Performance Testing

Run multiple concurrent requests:
```python
# Use the provided test_mcp.py script for automated testing
python test_mcp.py --concurrent 10
```

## Audit Log Verification

Check the MCP server logs for audit entries:
```bash
docker logs mcp_server | grep "Audit:"
```

Each operation should have a complete audit trail with:
- Timestamp
- Correlation ID
- Action
- Request payload
- Response payload
- Status