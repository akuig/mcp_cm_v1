# Product Service Links Table Fix

## Problem
The catalog manager is looking for a `product_service_links` table that doesn't exist in the database. This table is critical for linking product offerings to their underlying service specifications.

## Solution Files Created

### 1. `create_product_service_links.sql`
Complete SQL script that:
- Creates the `product_service_links` table with proper structure
- Adds foreign key constraints to product_offerings and service_specifications
- Creates performance indexes
- Populates 25 product-to-service mappings for all 14 products
- Includes verification queries to check the data

### 2. `apply_product_service_links.sh` 
Full bash script with error checking and status messages

### 3. `quick_fix_links.sh`
Simple one-liner script for quick execution

## How to Apply the Fix

### Option 1: Using the Full Script (Recommended)
```bash
cd /Users/joe/dev/mcp_cm_v1
chmod +x apply_product_service_links.sh
./apply_product_service_links.sh
```

### Option 2: Using the Quick Script
```bash
cd /Users/joe/dev/mcp_cm_v1
chmod +x quick_fix_links.sh
./quick_fix_links.sh
```

### Option 3: Direct psql Command
```bash
cd /Users/joe/dev/mcp_cm_v1
PGPASSWORD="telecom_catalog" psql -h localhost -U telecom_user -d telecom_catalog -f create_product_service_links.sql
```

### Option 4: Manual psql Session
```bash
psql -h localhost -U telecom_user -d telecom_catalog
# Enter password: telecom_catalog
\i create_product_service_links.sql
```

## What Gets Created

### Table Structure
- **Table Name**: `product_service_links`
- **Primary Key**: Auto-incrementing `id`
- **Foreign Keys**: 
  - `product_offering_id` → product_offerings(id)
  - `service_specification_id` → service_specifications(id)
- **Unique Constraint**: Each product-service pair can only exist once
- **Indexes**: 3 indexes for query performance

### Data Inserted (25 Links)

**Internet Packages (5 products → 5 services):**
- pkg_fiber_500 → fiber_500
- pkg_fiber_1000 → fiber_1000
- pkg_fiber_2000 → fiber_2000
- pkg_cable_400 → cable_400
- pkg_wireless_300 → wireless_300

**TV Packages (3 products → 3 services):**
- pkg_tv_basic → tv_basic
- pkg_tv_premium → tv_premium
- pkg_tv_streaming → tv_streaming

**Mobile Packages (2 products → 1 service):**
- pkg_mobile_family → mobile_unlimited
- pkg_mobile_unlimited → mobile_unlimited

**Bundle Packages (4 products → 14 service links):**
- **pkg_triple_play** (3 services):
  - fiber_1000 (primary)
  - tv_premium
  - phone_basic

- **pkg_double_play_it** (2 services):
  - fiber_500 (primary)
  - tv_premium

- **pkg_smart_home** (3 services):
  - fiber_1000 (primary)
  - tv_basic
  - security_premium

- **pkg_everything** (5 services):
  - fiber_2000 (primary)
  - tv_ultimate
  - phone_international
  - mobile_unlimited
  - security_premium

## Verification

After running the script, you should see output from these queries:
- Total links: 25
- Products with services: 14
- Services in use: 12 (out of 22 available)
- Services NOT in use: 10 (dsl services, some mobile/wireless tiers, etc.)

## Testing

After applying the fix, test with:
```bash
# Test listing offerings with services
# This should now work without errors
curl -X GET "http://localhost:8080/catalog/offerings?include_services=true"
```

Or via the MCP tools:
```
list_product_offerings with include_services=true
```

## Notes

- The script is idempotent - safe to run multiple times
- Uses `INSERT` statements (not `INSERT ... ON CONFLICT`) for clarity
- If the table already exists, it will skip creation
- Duplicate inserts will fail due to unique constraint (safe)

## Troubleshooting

### Error: "relation already exists"
The table already exists. This is safe to ignore.

### Error: "duplicate key value violates unique constraint"
Some links already exist. This is safe to ignore.

### Error: "database does not exist"
Create the database first or run the init scripts.

### Error: "connection refused"
PostgreSQL is not running. Start it with:
```bash
docker-compose up -d postgres
# or
pg_ctl start
```
