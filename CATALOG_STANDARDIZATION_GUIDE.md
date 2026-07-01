# Catalog Standardization and Optimization Guide

## 📊 Overview

This guide provides SQL scripts and tools to standardize your telecom catalog across multiple servers, fix critical issues, and optimize performance.

## 🚨 Critical Issues Addressed

### Server 2 (Fanore MCP)
- **CRITICAL**: Business Fiber Pro product (`pkg_enterprise_fiber_1000`) not linked to service specification
- Missing business fiber coverage data
- Incomplete phone and security coverage

### Server 1 (MCP Local)
- Missing business/enterprise product offerings
- Missing enterprise fiber service specification

## 📁 Files Created

### SQL Migration Scripts

1. **fix_server2_critical.sql** ⭐ **CRITICAL - RUN FIRST**
   - Fixes broken Business Fiber Pro product
   - Links product to enterprise_fiber_1000 service
   - Adds business fiber coverage
   - Fills phone and security coverage gaps
   - **Impact**: Makes Business Fiber Pro orderable

2. **upgrade_server1_to_match_server2.sql**
   - Adds enterprise fiber service spec to Server 1
   - Adds Business Fiber Pro product to Server 1
   - Creates proper product-service link
   - Adds business fiber coverage
   - **Impact**: Server 1 gains business capabilities

3. **standardize_both_servers.sql**
   - Ensures both servers have identical catalogs
   - 23 service specifications
   - 15 product offerings
   - 24 product-service links
   - **Impact**: Complete standardization

4. **optional_deprecate_unused_specs.sql** (Optional)
   - Marks 11 unused service specs as deprecated
   - Reduces complexity by 48%
   - Keeps data but marks inactive
   - **Impact**: Cleaner, simpler catalog

### Bash Execution Scripts

5. **execute_standardization.sh** ⭐ **RECOMMENDED**
   - Interactive wizard for all phases
   - Runs all scripts in correct order
   - Includes verification steps
   - **Use this for guided setup**

6. **quick_fix_server2.sh**
   - One-command fix for Server 2 critical issue
   - Use when you only need the urgent fix
   - **Use this if Server 2 is broken NOW**

7. **docker_fix_links.sh** (from earlier)
   - Creates product_service_links table
   - Already executed on both servers

## 🚀 Quick Start

### Option 1: Complete Standardization (Recommended)

Run the interactive wizard that handles everything:

```bash
cd /Users/joe/dev/mcp_cm_v1
chmod +x execute_standardization.sh
./execute_standardization.sh
```

The wizard will guide you through:
1. ✅ Fixing Server 2 critical issue
2. ✅ Upgrading Server 1
3. ✅ Standardizing both servers
4. ⚠️ Optional: Deprecating unused specs

### Option 2: Server 2 Critical Fix Only

If you just need to fix the broken Business Fiber Pro product:

```bash
chmod +x quick_fix_server2.sh
./quick_fix_server2.sh
```

### Option 3: Manual Execution

Run scripts individually using Docker:

```bash
# Fix Server 2
docker cp fix_server2_critical.sql telecom_postgres:/tmp/
docker exec telecom_postgres psql -U telecom_user -d telecom_catalog -f /tmp/fix_server2_critical.sql

# Upgrade Server 1
docker cp upgrade_server1_to_match_server2.sql telecom_postgres:/tmp/
docker exec telecom_postgres psql -U telecom_user -d telecom_catalog -f /tmp/upgrade_server1_to_match_server2.sql

# Standardize both
docker cp standardize_both_servers.sql telecom_postgres:/tmp/
docker exec telecom_postgres psql -U telecom_user -d telecom_catalog -f /tmp/standardize_both_servers.sql

# Optional: Deprecate unused specs
docker cp optional_deprecate_unused_specs.sql telecom_postgres:/tmp/
docker exec telecom_postgres psql -U telecom_user -d telecom_catalog -f /tmp/optional_deprecate_unused_specs.sql
```

## 📊 What Each Phase Does

### Phase 1: Fix Server 2 Critical Issue

**Problem**: Business Fiber Pro product exists but has no service link
- Product ID: `pkg_enterprise_fiber_1000`
- Price: $179.99/month + $299.99 setup
- Status: ❌ Cannot be ordered (no service link)

**Solution**:
```sql
-- Links product to service
INSERT INTO product_service_links 
  (product_offering_id, service_specification_id, is_primary)
VALUES 
  ('pkg_enterprise_fiber_1000', 'enterprise_fiber_1000', true);

-- Adds coverage at premium fiber locations
```

**Result**: ✅ Business Fiber Pro becomes orderable

### Phase 2: Upgrade Server 1

**Current State**: Server 1 lacks business offerings

**Additions**:
- Enterprise Fiber 1 Gbps service spec
- Business Fiber Pro product offering  
- Product-service link
- Business fiber coverage

**Result**: ✅ Both servers have business capabilities

### Phase 3: Complete Standardization

**Ensures**:
- 23 identical service specifications
- 15 identical product offerings
- 24 identical product-service links
- 7 geographic locations with coverage
- Zero orphaned products

**Result**: ✅ Catalog consistency across servers

### Phase 4: Deprecate Unused Specs (Optional)

**Marks these as deprecated**:
- cable_100, cable_200 (superseded by cable_400)
- dsl_25, dsl_50 (legacy technology)
- wireless_50, wireless_150 (only 300 used)
- mobile_5gb, mobile_25gb (only unlimited offered)
- security_basic (only premium offered)

**Benefits**:
- 48% reduction in active specs (23 → 12)
- Clearer product catalog
- Easier maintenance
- No impact on existing products

**Result**: ✅ Simpler, cleaner catalog

## ✅ Verification

After running scripts, verify success:

```bash
# Check catalog state
docker exec telecom_postgres psql -U telecom_user -d telecom_catalog -c "
SELECT 
  (SELECT COUNT(*) FROM service_specifications) as specs,
  (SELECT COUNT(*) FROM product_offerings WHERE is_active = true) as products,
  (SELECT COUNT(*) FROM product_service_links) as links;
"

# Check for orphaned products (should be 0)
docker exec telecom_postgres psql -U telecom_user -d telecom_catalog -c "
SELECT COUNT(*) as orphaned_products
FROM product_offerings po
LEFT JOIN product_service_links psl ON po.id = psl.product_offering_id
WHERE po.is_active = true AND psl.id IS NULL;
"

# Test Business Fiber Pro
docker exec telecom_postgres psql -U telecom_user -d telecom_catalog -c "
SELECT po.name, ss.name as service, COUNT(*) as coverage_locations
FROM product_offerings po
JOIN product_service_links psl ON po.id = psl.product_offering_id
JOIN service_specifications ss ON psl.service_specification_id = ss.id
LEFT JOIN service_coverage_new sc ON sc.service_type = 'business_fiber_internet'
WHERE po.id = 'pkg_enterprise_fiber_1000'
GROUP BY po.name, ss.name;
"
```

## 📈 Expected Results

### After Phase 1 (Server 2 Fix)
```
✓ pkg_enterprise_fiber_1000 linked to enterprise_fiber_1000
✓ Business fiber coverage at 3-5 locations
✓ Phone coverage at 6-7 locations
✓ Security coverage at 4-5 locations
✓ Zero orphaned products
```

### After Phase 2 (Server 1 Upgrade)
```
Server 1:
✓ 23 service specifications
✓ 15 product offerings
✓ 24 product-service links
✓ All products properly linked
```

### After Phase 3 (Standardization)
```
Both Servers:
✓ Identical 23 service specifications
✓ Identical 15 product offerings
✓ Identical 24 product-service links
✓ Identical 7 geographic locations
✓ Zero orphaned products
✓ Zero missing specifications
```

### After Phase 4 (Optional Deprecation)
```
Both Servers:
✓ 12 active service specifications
✓ 11 deprecated specifications
✓ 52% spec utilization (12/23 active)
✓ Cleaner catalog
```

## 🎯 Catalog Summary

### Service Specifications (23 total)

**Internet (12 specs)**
- Fiber: fiber_500, fiber_1000, fiber_2000
- Cable: cable_100, cable_200, cable_400
- DSL: dsl_25, dsl_50
- Wireless: wireless_50, wireless_150, wireless_300
- Business: enterprise_fiber_1000

**TV (4 specs)**
- tv_basic, tv_premium, tv_streaming, tv_ultimate

**Mobile (3 specs)**
- mobile_5gb, mobile_25gb, mobile_unlimited

**Phone (2 specs)**
- phone_basic, phone_international

**Security (2 specs)**
- security_basic, security_premium

### Product Offerings (15 total)

**Internet (5 products)**
1. TeleCo Fiber 500 - $59.99/mo
2. TeleCo Fiber Gig - $79.99/mo
3. TeleCo Fiber Pro - $129.99/mo
4. TeleCo Cable Max - $49.99/mo
5. TeleCo 5G Home - $69.99/mo

**TV (3 products)**
6. TeleCo Basic TV - $29.99/mo
7. TeleCo Premium TV - $79.99/mo
8. TeleCo Stream TV - $39.99/mo

**Mobile (2 products)**
9. TeleCo Family Mobile - $120/mo
10. TeleCo Unlimited Mobile - $65/mo

**Bundles (4 products)**
11. TeleCo Triple Play - $99.99/mo (Internet + TV + Phone)
12. TeleCo Internet + TV - $89.99/mo
13. TeleCo Smart Home - $119.99/mo (Internet + TV + Security)
14. TeleCo Everything - $149.99/mo (5 services)

**Business (1 product)**
15. TeleCo Business Fiber Pro - $179.99/mo ⭐ **NEW**

## 🔍 Troubleshooting

### Issue: "relation product_service_links does not exist"

**Solution**: Run the original table creation script first:
```bash
./docker_fix_links.sh
```

### Issue: "Business product still not linked"

**Check**:
```bash
docker exec telecom_postgres psql -U telecom_user -d telecom_catalog -c "
SELECT * FROM product_service_links 
WHERE product_offering_id = 'pkg_enterprise_fiber_1000';
"
```

**Fix**: Re-run Phase 1:
```bash
./quick_fix_server2.sh
```

### Issue: "Container not running"

**Solution**:
```bash
docker-compose up -d
docker ps | grep telecom
```

### Issue: "Permission denied"

**Solution**:
```bash
chmod +x execute_standardization.sh
chmod +x quick_fix_server2.sh
```

## 📋 Maintenance

### Regular Health Checks

Run periodically to ensure catalog health:

```bash
# Via MCP tools
sync_catalog_data with sync_type="integrity_check"

# Via SQL
docker exec telecom_postgres psql -U telecom_user -d telecom_catalog -c "
SELECT 
  COUNT(DISTINCT po.id) as products,
  COUNT(DISTINCT psl.product_offering_id) as products_with_services,
  COUNT(DISTINCT po.id) - COUNT(DISTINCT psl.product_offering_id) as orphaned
FROM product_offerings po
LEFT JOIN product_service_links psl ON po.id = psl.product_offering_id
WHERE po.is_active = true;
"
```

### Adding New Products

When adding new products, always:
1. Create service specification first
2. Create product offering
3. Link product to service immediately
4. Add coverage data
5. Verify with integrity check

### Backup Before Changes

```bash
docker exec telecom_postgres pg_dump -U telecom_user telecom_catalog > catalog_backup_$(date +%Y%m%d).sql
```

## 🎓 Key Learnings

1. **Always link products to services** - Unlinked products cannot be ordered
2. **Add coverage data** - Products need coverage to be available at locations
3. **Verify after changes** - Use integrity checks to catch issues early
4. **Standardize across servers** - Inconsistent catalogs cause confusion
5. **Deprecate thoughtfully** - Mark unused specs as deprecated rather than deleting

## 📞 Support

If issues persist:
1. Check Docker logs: `docker logs telecom_postgres`
2. Verify database connection: `docker exec -it telecom_postgres psql -U telecom_user -d telecom_catalog`
3. Review error messages in SQL output
4. Run integrity checks via MCP tools

## 🎉 Success Criteria

Your catalog standardization is complete when:
- ✅ All 15 products have service links
- ✅ Zero orphaned products
- ✅ Business Fiber Pro is orderable
- ✅ Both servers have identical catalogs
- ✅ Integrity checks pass without warnings
- ✅ Service qualification works correctly

---

**Last Updated**: 2025-10-11  
**Version**: 1.0  
**Compatible with**: PostgreSQL 15, Docker, TM Forum APIs
