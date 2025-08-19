#!/usr/bin/env python3
"""
Test script for Order Lifecycle Management Tools
Tests the new TMF622-compliant order management functions
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, Any

# Configuration
BASE_URL = "http://localhost:8080"
CUSTOMER_ID = "8452934"  # Jane Doe

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text: str):
    """Print a formatted header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.ENDC}")

def print_success(text: str):
    """Print success message"""
    print(f"{Colors.GREEN}✅ {text}{Colors.ENDC}")

def print_error(text: str):
    """Print error message"""
    print(f"{Colors.RED}❌ {text}{Colors.ENDC}")

def print_info(text: str):
    """Print info message"""
    print(f"{Colors.YELLOW}ℹ️  {text}{Colors.ENDC}")

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
    
    if response.status_code == 201 or response.status_code == 200:
        order = response.json()
        print_success(f"Order created: {order['id']}")
        print(f"   External ID: {order.get('externalId')}")
        print(f"   Status: {order.get('state', order.get('status'))}")
        return order['id']
    else:
        print_error(f"Failed to create order: {response.status_code}")
        print(response.text)
        return None

def test_update_status(order_id: str, new_status: str, reason: str = None):
    """Test updating order status"""
    print_info(f"Updating order {order_id} to status '{new_status}'...")
    
    update_data = {"state": new_status}
    if reason:
        update_data["reason"] = reason
    
    response = requests.patch(f"{BASE_URL}/tmf622/productOrder/{order_id}", json=update_data)
    
    if response.status_code == 200:
        order = response.json()
        print_success(f"Order status updated to '{order.get('state', order.get('status'))}'")
        if reason:
            print(f"   Reason: {reason}")
    else:
        print_error(f"Failed to update status: {response.status_code}")
        print(response.text)

def test_cancel_order(order_id: str):
    """Test cancelling an order"""
    print_info(f"Cancelling order {order_id}...")
    
    response = requests.post(f"{BASE_URL}/tmf622/productOrder/{order_id}/cancel")
    
    if response.status_code == 200:
        order = response.json()
        print_success(f"Order cancelled successfully")
        print(f"   Status: {order.get('state', order.get('status'))}")
        print(f"   Cancellation Date: {order.get('cancellationDate')}")
    else:
        print_error(f"Failed to cancel order: {response.status_code}")
        print(response.text)

def test_delete_order(order_id: str):
    """Test deleting an order"""
    print_info(f"Deleting order {order_id}...")
    
    response = requests.delete(f"{BASE_URL}/tmf622/productOrder/{order_id}")
    
    if response.status_code == 200:
        result = response.json()
        print_success(f"Order deleted successfully")
        print(f"   Message: {result.get('message')}")
        print(f"   Deleted At: {result.get('deletedAt')}")
    else:
        print_error(f"Failed to delete order: {response.status_code}")
        print(response.text)

def main():
    """Main test function"""
    print_header("Order Lifecycle Management Test Suite")
    print(f"Testing against: {BASE_URL}")
    print(f"Customer ID: {CUSTOMER_ID}")
    
    try:
        # Create and test order lifecycle
        order_id = create_order()
        if order_id:
            time.sleep(1)
            test_update_status(order_id, "acknowledged", "Order received")
            time.sleep(1)
            test_update_status(order_id, "inProgress", "Processing order")
            time.sleep(1)
            test_cancel_order(order_id)
            time.sleep(1)
            test_delete_order(order_id)
            
            print_header("Test Suite Complete!")
            print_success("All order lifecycle management tests passed")
        
    except Exception as e:
        print_error(f"Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()