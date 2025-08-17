#!/usr/bin/env python3
"""
Demo Database Reset Script for Telepath AI Catalog Manager
Cleans up all demo data to prepare for fresh demonstrations
"""

import asyncio
import aiohttp
import json
import sys
from datetime import datetime
from typing import List, Dict, Optional

# Configuration
CATALOG_MANAGER_URL = "http://catalog-manager:8080"  # Adjust URL as needed
DEFAULT_TIMEOUT = 30

class DemoReset:
    def __init__(self, base_url: str = CATALOG_MANAGER_URL):
        self.base_url = base_url
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def ensure_session(self):
        """Ensure aiohttp session is created"""
        if self.session is None:
            self.session = aiohttp.ClientSession()
    
    async def cleanup_session(self):
        """Cleanup aiohttp session"""
        if self.session:
            await self.session.close()
    
    async def get_all_orders(self) -> List[Dict]:
        """Retrieve all orders from the system"""
        await self.ensure_session()
        try:
            url = f"{self.base_url}/api/orders"  # Adjust endpoint as needed
            async with self.session.get(url, timeout=DEFAULT_TIMEOUT) as response:
                if response.status == 200:
                    data = await response.json()
                    return data if isinstance(data, list) else []
                else:
                    print(f"⚠️  Could not retrieve orders: HTTP {response.status}")
                    return []
        except Exception as e:
            print(f"⚠️  Error retrieving orders: {str(e)}")
            return []
    
    async def delete_order(self, order_id: str) -> bool:
        """Delete a specific order"""
        await self.ensure_session()
        try:
            url = f"{self.base_url}/api/orders/{order_id}"  # Adjust endpoint as needed
            async with self.session.delete(url, timeout=DEFAULT_TIMEOUT) as response:
                if response.status in [200, 204, 404]:  # 404 means already deleted
                    return True
                else:
                    print(f"⚠️  Could not delete order {order_id}: HTTP {response.status}")
                    return False
        except Exception as e:
            print(f"⚠️  Error deleting order {order_id}: {str(e)}")
            return False
    
    async def get_all_service_activations(self) -> List[Dict]:
        """Retrieve all service activations"""
        await self.ensure_session()
        try:
            url = f"{self.base_url}/api/services"  # Adjust endpoint as needed
            async with self.session.get(url, timeout=DEFAULT_TIMEOUT) as response:
                if response.status == 200:
                    data = await response.json()
                    return data if isinstance(data, list) else []
                else:
                    print(f"⚠️  Could not retrieve services: HTTP {response.status}")
                    return []
        except Exception as e:
            print(f"⚠️  Error retrieving services: {str(e)}")
            return []
    
    async def deactivate_service(self, service_id: str) -> bool:
        """Deactivate/delete a specific service"""
        await self.ensure_session()
        try:
            url = f"{self.base_url}/api/services/{service_id}"  # Adjust endpoint as needed
            async with self.session.delete(url, timeout=DEFAULT_TIMEOUT) as response:
                if response.status in [200, 204, 404]:  # 404 means already deleted
                    return True
                else:
                    print(f"⚠️  Could not deactivate service {service_id}: HTTP {response.status}")
                    return False
        except Exception as e:
            print(f"⚠️  Error deactivating service {service_id}: {str(e)}")
            return False
    
    async def reset_customer_orders(self, customer_id: str = "8452934") -> bool:
        """Reset specific demo customer's orders"""
        print(f"🔄 Resetting orders for customer {customer_id}...")
        
        # Note: This would use the MCP tools if available
        # For now, we'll use direct API calls
        try:
            # Get customer orders (adjust based on your API)
            await self.ensure_session()
            url = f"{self.base_url}/api/customers/{customer_id}/orders"
            async with self.session.get(url, timeout=DEFAULT_TIMEOUT) as response:
                if response.status == 200:
                    orders = await response.json()
                    deleted_count = 0
                    for order in orders:
                        order_id = order.get('id')
                        if order_id and await self.delete_order(order_id):
                            deleted_count += 1
                            print(f"  ✅ Deleted order: {order_id}")
                    print(f"📋 Deleted {deleted_count} orders for customer {customer_id}")
                    return True
                else:
                    print(f"⚠️  Could not get customer orders: HTTP {response.status}")
                    return False
        except Exception as e:
            print(f"⚠️  Error resetting customer orders: {str(e)}")
            return False
    
    async def database_cleanup(self) -> bool:
        """Direct database cleanup - adjust SQL based on your schema"""
        print("🗄️  Performing direct database cleanup...")
        
        # This is a template - adjust based on your actual database setup
        cleanup_queries = [
            "DELETE FROM product_orders WHERE external_id LIKE 'ORD-8452934-%';",
            "DELETE FROM service_activations WHERE service_name LIKE '%Jane Doe%';",
            "DELETE FROM audit_logs WHERE action IN ('product_ordering', 'service_activation') AND timestamp > CURRENT_DATE;",
            # Add more cleanup queries as needed
        ]
        
        print("📝 SQL cleanup queries to run:")
        for i, query in enumerate(cleanup_queries, 1):
            print(f"  {i}. {query}")
        
        print("⚠️  Execute these queries manually in your database management tool")
        return True
    
    async def full_reset(self) -> bool:
        """Perform a complete demo reset"""
        print("🚀 Starting Demo Database Reset")
        print("=" * 50)
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"⏰ Reset started at: {timestamp}")
        
        success = True
        
        # 1. Reset specific demo customer orders
        print("\n📋 Step 1: Cleaning up demo customer orders...")
        if not await self.reset_customer_orders("8452934"):
            success = False
        
        # 2. Clean up any orphaned service activations
        print("\n🔧 Step 2: Cleaning up service activations...")
        services = await self.get_all_service_activations()
        deactivated_count = 0
        for service in services:
            service_id = service.get('id')
            service_name = service.get('name', '')
            # Only clean up demo services (adjust criteria as needed)
            if service_id and ('Jane Doe' in service_name or 'demo' in service_name.lower()):
                if await self.deactivate_service(service_id):
                    deactivated_count += 1
                    print(f"  ✅ Deactivated service: {service_id}")
        print(f"🔧 Deactivated {deactivated_count} demo services")
        
        # 3. Database cleanup instructions
        print("\n🗄️  Step 3: Database cleanup...")
        await self.database_cleanup()
        
        print("\n" + "=" * 50)
        if success:
            print("✅ Demo reset completed successfully!")
            print("🎯 System ready for fresh demonstration")
        else:
            print("⚠️  Demo reset completed with some warnings")
            print("🔍 Check the output above for any issues")
        
        end_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"⏰ Reset finished at: {end_timestamp}")
        
        return success

async def main():
    """Main entry point"""
    print("🎭 Telepath AI - Demo Database Reset Utility")
    print()
    
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='Reset demo database for fresh demonstrations')
    parser.add_argument('--url', default=CATALOG_MANAGER_URL, 
                       help=f'Catalog Manager URL (default: {CATALOG_MANAGER_URL})')
    parser.add_argument('--customer-id', default='8452934',
                       help='Demo customer ID to reset (default: 8452934)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be deleted without actually deleting')
    
    args = parser.parse_args()
    
    if args.dry_run:
        print("🔍 DRY RUN MODE - No actual changes will be made")
        print()
    
    reset_tool = DemoReset(base_url=args.url)
    
    try:
        if args.dry_run:
            print("Would reset demo data for:")
            print(f"  Customer ID: {args.customer_id}")
            print(f"  Base URL: {args.url}")
            print("\nRun without --dry-run to perform actual reset")
            return True
        else:
            success = await reset_tool.full_reset()
            return success
    
    except KeyboardInterrupt:
        print("\n⚠️  Reset cancelled by user")
        return False
    except Exception as e:
        print(f"\n❌ Reset failed with error: {str(e)}")
        return False
    finally:
        await reset_tool.cleanup_session()

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Fatal error: {str(e)}")
        sys.exit(1)
