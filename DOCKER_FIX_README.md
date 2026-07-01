# Product Service Links Table Fix - DOCKER VERSION

## Problem
The catalog manager is looking for a `product_service_links` table that doesn't exist in the database. This table is critical for linking product offerings to their underlying service specifications.

## ⚠️ Important: Docker Setup
Your PostgreSQL is running in Docker with:
- Container name: `telecom_postgres`
- Password: `telecom_pass` (from docker-compose.yml)
- Database: `telecom_catalog`
- Port: 5432 (mapped to localhost:5432)

## Solution Files Created

### 1. `create_product_service_links.sql`
Complete SQL script with table creation and 25 product-to-service mappings

### 2. `docker_fix_links.sh` ⭐ **RECOMMENDED**
Full featured script that uses Docker exec (no localhost connection issues)

### 3. `quick_docker_fix.sh` 
One-liner Docker version for quick execution

### 4. `localhost_fix_links.sh`
Alternative that connects via localhost:5432 (if psql client is installed)

## 🚀 How to Apply (Choose One Method)

### Method 1: Docker Exec Script (Recommended) ⭐
```bash
cd /Users/joe/dev/mcp_cm_v1
chmod +x docker_fix_links.sh
./docker_fix_links.sh
```

### Method 2: Quick Docker One-Liner
```bash
cd /Users/joe/dev/mcp_cm_v1
chmod +x quick_docker_fix.sh
./quick_docker_fix.sh
```

### Method 3: Direct Docker Commands
```bash
cd /Users/joe/dev/mcp_cm_v1

# Copy SQL file to container
docker cp create_product_service_links.sql telecom_postgres:/tmp/

# Execute inside container
docker exec telecom_postgres psql -U telecom_user -d telecom_catalog -f /tmp/create_product_service_links.sql

# Cleanup
docker exec telecom_postgres rm /tmp/create_product_service_links.sql
```

### Method 4: Interactive Docker Shell
```bash
# Enter the container
docker exec -it telecom_postgres bash

# Inside container, run:
psql -U telecom_user -d telecom_catalog

# Then paste or run the SQL commands from create_product_service_links.sql
```

### Method 5: Localhost Connection (if psql installed locally)
```bash
cd /Users/joe/dev/mcp_cm_v1
chmod +x localhost_fix_links.sh
./localhost_fix_links.sh
```

Or manually:
```bash
PGPASSWORD="telecom_pass" psql -h localhost -U telecom_user -d telecom_catalog -f create_product_service_links.sql
```

## Prerequisites

Make sure Docker containers are running:
```bash
docker-compose up -d

# Verify containers are running
docker ps | grep telecom

# You should see:
# - telecom_postgres
# - catalog_manager  
# - mcp_server
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

After running the script, verify it worked:

```bash
# Check table exists
docker exec telecom_postgres psql -U telecom_user -d telecom_catalog -c "\dt product_service_links"

# Count links
docker exec telecom_postgres psql -U telecom_user -d telecom_catalog -c "SELECT COUNT(*) FROM product_service_links;"

# Show all mappings
docker exec telecom_postgres psql -U telecom_user -d telecom_catalog -c "SELECT po.name as product, ss.name as service, psl.is_primary FROM product_service_links psl JOIN product_offerings po ON psl.product_offering_id = po.id JOIN service_specifications ss ON psl.service_specification_id = ss.id ORDER BY po.name;"
```

Expected results:
- Total links: 25
- Products with services: 14
- Services in use: 12 (out of 22 available)

## Testing the Fix

After applying, test that the catalog manager works:

```bash
# Test via curl
curl -X GET "http://localhost:8080/catalog/offerings?include_services=true"

# Should now return offerings WITH their service details instead of an error
```

Or test via MCP tools - this command should now work:
```
list_product_offerings with include_services=true
```

## Troubleshooting

### Error: "Cannot find container telecom_postgres"
```bash
docker-compose up -d
docker ps  # Verify containers are running
```

### Error: "Permission denied"
```bash
chmod +x docker_fix_links.sh
chmod +x quick_docker_fix.sh
chmod +x localhost_fix_links.sh
```

### Error: "relation already exists"
The table already exists - this is safe. The fix has already been applied.

### Error: "database does not exist"
The database wasn't initialized properly. Restart containers:
```bash
docker-compose down
docker-compose up -d
# Wait 30 seconds for initialization
./docker_fix_links.sh
```

### Error: Connection refused on localhost
Use the Docker exec method instead of localhost connection:
```bash
./docker_fix_links.sh
```

### Verify Docker is running PostgreSQL
```bash
docker ps | grep postgres
docker logs telecom_postgres | tail -20
```

## Quick Reference

**Fastest method:**
```bash
bash quick_docker_fix.sh
```

**Most reliable method:**
```bash
bash docker_fix_links.sh
```

**Restart everything from scratch:**
```bash
docker-compose down
docker-compose up -d
# Wait 30 seconds
bash docker_fix_links.sh
```
