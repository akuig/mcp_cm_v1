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

3. Test the MCP server:
```bash
# Option 1: Use MCP Inspector (recommended for interactive testing)
make inspector

# Option 2: Run automated tests
python test_mcp.py

# Option 3: Test with curl
make test-curl
```

## Using MCP Inspector

The MCP Inspector can be used with the HTTP streaming server through a bridge:

1. Make sure services are running: `make up`
2. Run: `make inspector`
3. The Inspector will open with access to all tools:
   - `service_qualification` - Check service availability
   - `customer_management` - Look up customer information
   - `product_ordering` - Create orders
   - `service_activation` - Activate services

The bridge (`mcp_bridge.py`) translates between the Inspector's stdio interface and the HTTP streaming server.

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

Check service health:
```bash
# Check all services
make health

# Test MCP endpoints directly
curl http://localhost:8090/health
```

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

## Testing with HTTP Streaming Client

You can test the MCP server directly with curl:

```bash
# Initialize MCP connection
curl -X POST http://localhost:8090/mcp/stream \
  -H "Content-Type: application/json" \
  -H "Accept: application/json-stream" \
  -d '{
    "jsonrpc": "2.0",
    "method": "initialize",
    "params": {},
    "id": 1
  }'

# List available tools
curl -X POST http://localhost:8090/mcp/stream \
  -H "Content-Type: application/json" \
  -H "Accept: application/json-stream" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/list",
    "params": {},
    "id": 2
  }'

# Call a tool (service qualification)
curl -X POST http://localhost:8090/mcp/stream \
  -H "Content-Type: application/json" \
  -H "Accept: application/json-stream" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "service_qualification",
      "arguments": {
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
    },
    "id": 3
  }'
```

The responses will be streamed back using chunked transfer encoding.

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