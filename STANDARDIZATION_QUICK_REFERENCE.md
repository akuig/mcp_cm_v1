# Catalog Standardization - Quick Reference

## 🚀 Quick Start (Choose One)

### Option 1: Complete Setup (Recommended)
```bash
bash make_standardization_scripts_executable.sh
./execute_standardization.sh
```

### Option 2: Fix Server 2 Only (Urgent)
```bash
bash quick_fix_server2.sh
```

### Option 3: Manual Step-by-Step
```bash
# Fix Server 2
docker cp fix_server2_critical.sql telecom_postgres:/tmp/
docker exec telecom_postgres psql -U telecom_user -d telecom_catalog -f /tmp/fix_server2_critical.sql

# Upgrade Server 1
docker cp upgrade_server1_to_match_server2.sql telecom_postgres:/tmp/
docker exec telecom_postgres psql -U telecom_user -d telecom_catalog -f /tmp/upgrade_server1_to_match_server2.sql

# Standardize
docker cp standardize_both_servers.sql telecom_postgres:/tmp/
docker exec telecom_postgres psql -U telecom_user -d telecom_catalog -f /tmp/standardize_both_servers.sql
```

## ✅ Verification

```bash
# Run all tests
bash test_standardization.sh

# Quick check
docker exec telecom_postgres psql -U telecom_user -d telecom_catalog -c "
SELECT COUNT(*) FROM product_service_links 
WHERE product_offering_id = 'pkg_enterprise_fiber_1000';"
# Expected: 1
```

## 🎯 What Gets Fixed

| Issue | Solution |
|-------|----------|
| Business product unlinked | Links pkg_enterprise_fiber_1000 → enterprise_fiber_1000 |
| Missing business coverage | Adds coverage at 3-5 premium locations |
| Server 1 lacks business | Adds business product + spec to Server 1 |
| Inconsistent catalogs | Standardizes both servers |
| Orphaned specs | Optional deprecation of 11 unused specs |

## 📊 Expected Final State

```
✅ 23 service specifications (or 12 if deprecated)
✅ 15 active product offerings
✅ 24 product-service links
✅ 7 geographic locations
✅ 0 orphaned products
✅ Business Fiber Pro operational
```

## 🔍 Troubleshooting

| Problem | Solution |
|---------|----------|
| Container not running | `docker-compose up -d` |
| Permission denied | `chmod +x *.sh` |
| Table doesn't exist | Run `./docker_fix_links.sh` first |
| Still orphaned products | Re-run `./quick_fix_server2.sh` |

## 📁 Files Created

**SQL Scripts:**
- `fix_server2_critical.sql` - Fix Server 2 NOW ⭐
- `upgrade_server1_to_match_server2.sql` - Add business to Server 1
- `standardize_both_servers.sql` - Complete sync
- `optional_deprecate_unused_specs.sql` - Clean up

**Bash Scripts:**
- `execute_standardization.sh` - Interactive wizard ⭐
- `quick_fix_server2.sh` - One-command fix
- `test_standardization.sh` - Verification tests

**Documentation:**
- `CATALOG_STANDARDIZATION_GUIDE.md` - Complete guide
- `STANDARDIZATION_QUICK_REFERENCE.md` - This file

## 🎓 Key Commands

```bash
# Make scripts executable
bash make_standardization_scripts_executable.sh

# Run complete standardization
./execute_standardization.sh

# Test everything
./test_standardization.sh

# Check catalog health via MCP
sync_catalog_data with sync_type="integrity_check"

# Backup database
docker exec telecom_postgres pg_dump -U telecom_user telecom_catalog > backup.sql
```

## ⚡ One-Liners

```bash
# Complete fix in one command
bash execute_standardization.sh

# Server 2 critical fix only
bash quick_fix_server2.sh

# Verify after fix
bash test_standardization.sh

# Check orphaned products
docker exec telecom_postgres psql -U telecom_user -d telecom_catalog -c "SELECT COUNT(*) FROM product_offerings po LEFT JOIN product_service_links psl ON po.id = psl.product_offering_id WHERE po.is_active = true AND psl.id IS NULL;"
```

## 📞 Support Checks

```bash
# Docker status
docker ps | grep telecom

# Database connection
docker exec -it telecom_postgres psql -U telecom_user -d telecom_catalog

# View logs
docker logs telecom_postgres | tail -50

# Restart containers
docker-compose restart
```

---

**See CATALOG_STANDARDIZATION_GUIDE.md for detailed documentation**
