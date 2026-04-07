# Testing Patterns

**Analysis Date:** 2026-04-07

## Test Framework

**Runner:**
- pytest 7.4.3
- pytest-asyncio 0.21.1 (for async/await test support)
- Config: No `pytest.ini` or `pyproject.toml` found - uses pytest defaults

**Assertion Library:**
- pytest built-in assertions and response status checking
- Manual assertion patterns using if-statements and logging

**Run Commands:**
```bash
python test_enhanced.py              # Run test suite directly
python test_order_lifecycle.py       # Run specific test scenario
pytest tests/                        # Run pytest suite (if organized under tests/)
```

## Test File Organization

**Location:**
- Test files co-located in root directory alongside source code
- Pattern: `test_*.py` in project root `/Users/joe/dev/mcp_cm_v1/`

**Naming:**
- Test files: `test_enhanced.py`, `test_order_lifecycle.py`, `test_complete_fixes.py`, `test_data_format_fix.py`
- Test classes: `EnhancedMCPTester`
- Test functions: `test_catalog_manager_health()`, `async def test_order_management()`

**Structure:**
```
mcp_cm_v1/
├── test_enhanced.py                 # Main async test suite
├── test_order_lifecycle.py           # Order lifecycle scenarios
├── test_complete_fixes.py            # Integration tests
├── test_data_format_fix.py           # Async API tests
├── mcp_fastmcp_server_extended.py    # Source under test
└── catalog_manager_enhanced.py       # Source under test
```

## Test Structure

**Suite Organization:**

Async class-based pattern from `test_enhanced.py` (lines 44-52):
```python
class EnhancedMCPTester:
    def __init__(self):
        self.session = None
        self.test_results = {
            'passed': 0,
            'failed': 0,
            'warnings': 0,
            'tests': []
        }

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
```

**Patterns:**

1. **Setup Pattern:** Context manager with async enter/exit for session management

2. **Test Method Pattern:** Individual async methods per test scenario
```python
async def test_catalog_manager_health(self):
    """Test basic catalog manager health"""
    print_test("Testing Catalog Manager health...")
    try:
        async with self.session.get(f"{CATALOG_MANAGER_URL}/health", timeout=TIMEOUT) as response:
            if response.status == 200:
                data = await response.json()
                if data.get('status') == 'healthy':
                    print_success("Catalog Manager is healthy")
                    self.record_test("catalog_manager_health", True)
                    return True
                else:
                    print_error(f"Catalog Manager returned unhealthy status: {data}")
                    self.record_test("catalog_manager_health", False, f"Unhealthy status: {data}")
                    return False
```

3. **Result Recording Pattern:**
```python
def record_test(self, name: str, passed: bool, message: str = "", warning: bool = False):
    """Record test result"""
    if warning:
        self.test_results['warnings'] += 1
        status = 'warning'
    elif passed:
        self.test_results['passed'] += 1
        status = 'passed'
    else:
        self.test_results['failed'] += 1
        status = 'failed'

    self.test_results['tests'].append({
        'name': name,
        'status': status,
        'message': message,
        'timestamp': datetime.utcnow().isoformat()
    })
```

4. **Teardown Pattern:** Implicit in context manager `__aexit__` (closes session)

## Mocking

**Framework:** No explicit mocking library found (no pytest-mock, unittest.mock usage)

**Patterns:**
- Direct HTTP calls to running servers (integration testing approach)
- Server configuration via environment: `CATALOG_MANAGER_URL = "http://localhost:8080"`
- MCP server URL: `MCP_SERVER_URL = "http://localhost:8090"`
- Tests assume servers are running and accessible

**What to Mock:**
- External HTTP dependencies: Not mocked - assumes running servers
- Database connections: Not directly called from tests - abstracted through HTTP APIs
- Async operations: Tests use real aiohttp sessions, no mocking

**What NOT to Mock:**
- HTTP calls to MCP and Catalog Manager APIs (integration testing preference)
- Actual async/await patterns (tests run real async code)
- Database state (tests hit live databases in containers)

## Fixtures and Factories

**Test Data:**

From `test_order_lifecycle.py` (lines 43-66):
```python
def create_order() -> str:
    """Create a test order"""
    print_info("Creating test order...")

    order_data = {
        "orderDate": datetime.now().strftime("%Y-%m-%d"),
        "externalId": f"TEST_LIFECYCLE_{int(time.time())}",
        "relatedParty": [{
            "id": CUSTOMER_ID,
            "role": "customer"
        }],
        "orderItem": [{
            "action": "add",
            "productOffering": {
                "id": "pkg_fiber_500"
            },
            "product": {
                "place": {
                    "streetNumber": "456",
                    "streetName": "Main Street",
                    "city": "Springfield"
                }
            }
        }]
    }

    response = requests.post(f"{BASE_URL}/tmf622/productOrder", json=order_data)
```

**Data Creation Functions:**
- `create_order()` - Returns order ID
- Factory functions embedded in test files, not in separate fixtures module
- Data uses hardcoded test customer ID: `CUSTOMER_ID = "8452934"` (Jane Doe)
- Timestamps generated at test time: `datetime.now().strftime("%Y-%m-%d")`
- External IDs use test prefix and timestamp: `f"TEST_LIFECYCLE_{int(time.time())}"`

**Location:**
- Fixtures/factories defined in test files themselves
- No `conftest.py` or shared fixtures directory
- Global constants at module level: `CATALOG_MANAGER_URL`, `CUSTOMER_ID`, `BASE_URL`

## Coverage

**Requirements:** Not enforced (no coverage config found)

**View Coverage:** Not documented (no coverage command in tests)

**Gap:** No coverage reporting configuration - tests run but coverage is not measured

## Test Types

**Unit Tests:**
- Not present in this codebase
- All tests are integration tests calling live HTTP endpoints

**Integration Tests:**
- Scope: Full API endpoints from catalog-manager and MCP server
- Approach:
  - Tests hit real running containers
  - Validate HTTP status codes and response format
  - Chain multiple operations (create -> update -> delete)
  - Verify data consistency across operations

Example from `test_enhanced.py` (lines 105-158):
```python
async def test_service_specifications_api(self):
    """Test service specifications APIs"""
    print_test("Testing Service Specifications API...")

    # Test GET /api/service-specifications
    try:
        async with self.session.get(f"{CATALOG_MANAGER_URL}/api/service-specifications?limit=5", timeout=TIMEOUT) as response:
            if response.status == 200:
                data = await response.json()
                if 'specifications' in data and isinstance(data['specifications'], list):
                    print_success(f"Retrieved {len(data['specifications'])} service specifications")
                    self.record_test("list_service_specifications", True, f"Found {len(data['specifications'])} specs")

                    # Test filtering
                    if data['specifications']:
                        first_spec = data['specifications'][0]
                        print_info(f"Sample spec: {first_spec.get('name')} ({first_spec.get('service_type')})")
    # ...

    # Test POST /api/service-specifications (create new spec)
    test_spec = {
        "name": "Test Enhanced Fiber",
        "service_type": "fiber_internet",
        "description": "Enhanced fiber service for automated testing"
    }

    try:
        async with self.session.post(f"{CATALOG_MANAGER_URL}/api/service-specifications",
                                   json=test_spec, timeout=TIMEOUT) as response:
            if response.status == 201:
                data = await response.json()
                print_success(f"Created service specification: {data.get('name')} (ID: {data.get('id')})")
                self.record_test("create_service_specification", True, f"Created spec ID: {data.get('id')}")
                return data.get('id')  # Return ID for linking tests
```

**E2E Tests:**
- Not formalized in separate directory
- Order lifecycle test (`test_order_lifecycle.py`) is end-to-end: create -> update -> cancel -> delete

Example from `test_order_lifecycle.py` (lines 135-170):
```python
async def main():
    """Run full lifecycle test"""
    print_header("Order Lifecycle Test Suite")

    # Test basic order creation
    order_id = create_order()
    if not order_id:
        print_error("Cannot proceed without order ID")
        sys.exit(1)

    # Test status updates
    test_update_status(order_id, "inProgress", "Customer confirmed service location")
    test_update_status(order_id, "pending", "Awaiting technician schedule")
    test_update_status(order_id, "completed", "Service installed and activated")

    # Test cancellation and deletion
    create_and_cancel_order()
    create_and_delete_order()
```

## Common Patterns

**Async Testing:**

From `test_enhanced.py` and `test_data_format_fix.py`:
```python
async with self.session.get(url, timeout=TIMEOUT) as response:
    result = await response.json()
    return result
```

Pattern uses context manager for resource cleanup and `await` for async operations.

**HTTP Status Testing:**

From `test_enhanced.py` (lines 85-99):
```python
async with self.session.get(f"{CATALOG_MANAGER_URL}/health", timeout=TIMEOUT) as response:
    if response.status == 200:
        data = await response.json()
        if data.get('status') == 'healthy':
            print_success("Catalog Manager is healthy")
            self.record_test("catalog_manager_health", True)
            return True
        else:
            print_error(f"Catalog Manager returned unhealthy status: {data}")
            self.record_test("catalog_manager_health", False, f"Unhealthy status: {data}")
            return False
    else:
        print_error(f"Catalog Manager health check failed with status {response.status}")
        self.record_test("catalog_manager_health", False, f"HTTP {response.status}")
        return False
```

Always check `response.status` first, then parse `await response.json()`, then validate response content.

**Error Testing:**

From `test_complete_fixes.py` (lines 20-43):
```python
try:
    # Test GET /tmf622/productOrder (should return array)
    response = requests.get(f"{CATALOG_MANAGER_URL}/tmf622/productOrder?limit=3")
    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"Response Type: {type(data)}")

        if isinstance(data, list):
            print("✅ SUCCESS: TMF622 correctly returns list format!")
            print(f"Number of orders: {len(data)}")
        else:
            print("❌ ISSUE: TMF622 should return list but returned dict")
            print(f"Data: {json.dumps(data, indent=2)[:200]}...")
    else:
        print(f"❌ ERROR: Status {response.status_code}")
        print(f"Response: {response.text}")

except Exception as e:
    print(f"❌ EXCEPTION: {str(e)}")
```

Tests catch broad exceptions, log the error, and print diagnostics.

**Parameter Validation Testing:**

From `test_enhanced.py` (lines 320-339):
```python
async def test_sync_catalog_api(self):
    """Test catalog sync and integrity checking"""
    print_test("Testing Catalog Sync API...")

    sync_data = {
        "sync_type": "integrity_check"
    }

    try:
        async with self.session.post(f"{CATALOG_MANAGER_URL}/api/sync-catalog-data",
                                   json=sync_data, timeout=TIMEOUT) as response:
            if response.status == 200:
                data = await response.json()
                print_success(f"Catalog sync completed successfully")
                print_info(f"Processed: {data.get('total_processed', 0)} records")
                print_info(f"Errors: {data.get('total_errors', 0)}")

                # Check results
                results = data.get('results', {})
                for check_type, result in results.items():
                    status = result.get('status', 'unknown')
                    count = result.get('count', 0)
                    print_info(f"  {check_type}: {status} ({count} items)")
```

Validates parameter handling and response parsing for complex objects.

## Test Reporting

**Format:** Color-coded terminal output via ANSI codes

Helper functions from `test_enhanced.py`:
```python
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    PURPLE = '\033[0;35m'
    CYAN = '\033[0;36m'
    NC = '\033[0m'  # No Color

def print_test(message: str):
    print(f"{Colors.BLUE}[TEST]{Colors.NC} {message}")

def print_success(message: str):
    print(f"{Colors.GREEN}[PASS]{Colors.NC} {message}")

def print_error(message: str):
    print(f"{Colors.RED}[FAIL]{Colors.NC} {message}")

def print_warning(message: str):
    print(f"{Colors.YELLOW}[WARN]{Colors.NC} {message}")

def print_info(message: str):
    print(f"{Colors.CYAN}[INFO]{Colors.NC} {message}")
```

**Result Aggregation:**

From `test_enhanced.py` (lines 47-52):
```python
self.test_results = {
    'passed': 0,
    'failed': 0,
    'warnings': 0,
    'tests': []
}
```

Tests accumulate in `self.test_results` list with status and timestamp.

---

*Testing analysis: 2026-04-07*
