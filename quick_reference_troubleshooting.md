# 🔧 Enhanced Catalog Manager - Quick Reference & Troubleshooting

## 🚀 **Quick Commands Reference**

### **Setup & Deployment**
```bash
# Complete fresh setup (new machine)
curl -O https://raw.githubusercontent.com/your-repo/setup_enhanced_catalog.sh
chmod +x setup_enhanced_catalog.sh
./setup_enhanced_catalog.sh

# Quick deployment (existing project)
cd /path/to/project
docker-compose up -d
./scripts/validate_deployment.sh

# Update Claude Desktop configuration
cp claude_desktop_config.json ~/.config/claude_desktop/config.json
# Then restart Claude Desktop
```

### **System Management**
```bash
# Start/Stop services
docker-compose up -d          # Start all services
docker-compose down           # Stop all services
docker-compose restart        # Restart all services

# Individual service management
docker-compose restart catalog-manager
docker-compose restart postgres

# View logs
docker-compose logs -f catalog-manager    # Follow catalog logs
docker-compose logs -f postgres           # Follow database logs
docker-compose logs --tail=100            # Last 100 lines all services
```

### **Health & Status Checks**
```bash
# Quick health check
curl http://localhost:8080/health

# Detailed status
docker-compose ps                    # Container status
docker stats                         # Resource usage
docker-compose exec postgres pg_isready -U telecom_user  # DB connectivity

# Comprehensive validation
./scripts/validate_deployment.sh     # Quick validation
python tests/test_complete_system.py # Full test suite
```

### **Database Operations**
```bash
# Connect to database
docker-compose exec postgres psql -U telecom_user -d telecom_catalog

# Common queries
docker-compose exec postgres psql -U telecom_user -d telecom_catalog -c "SELECT COUNT(*) FROM customers;"
docker-compose exec postgres psql -U telecom_user -d telecom_catalog -c "SELECT COUNT(*) FROM orders;"

# Backup/Restore
docker-compose exec postgres pg_dump -U telecom_user telecom_catalog > backup.sql
docker-compose exec -T postgres psql -U telecom_user telecom_catalog < backup.sql
```

## 🧪 **API Testing Quick Commands**

### **Core TMF APIs**
```bash
# TMF629 - Customer Management
curl "http://localhost:8080/tmf629/customer/8452934"

# TMF622 - Order Management (GET - returns list)
curl "http://localhost:8080/tmf622/productOrder?limit=5"

# TMF622 - Create Order (POST)
curl -X POST "http://localhost:8080/tmf622/productOrder" \
  -H "Content-Type: application/json" \
  -d '{
    "orderDate": "2025-07-30",
    "externalId": "TEST-001",
    "relatedParty": [{"id": "8452934", "role": "customer"}],
    "orderItem": [{
      "action": "add",
      "productOffering": {"id": "fiber-1gb"},
      "product": {
        "place": {
          "streetNumber": "456",
          "streetName": "Main Street",
          "city": "Springfield"
        }
      }
    }]
  }'

# TMF637 - Service Qualification
curl -X POST "http://localhost:8080/tmf637/serviceQualification" \
  -H "Content-Type: application/json" \
  -d '{
    "address": {
      "streetName": "Main Street",
      "streetNumber": "456",
      "city": "Springfield"
    },
    "serviceSpecification": {
      "id": "fiber-internet-premium",
      "name": "Fiber Internet Premium"
    }
  }'

# TMF640 - Service Activation
curl -X POST "http://localhost:8080/tmf640/serviceActivation" \
  -H "Content-Type: application/json" \
  -d '{
    "service": {
      "name": "Test Service",
      "serviceType": "fiber_internet",
      "place": {
        "streetNumber": "456",
        "streetName": "Main Street",
        "city": "Springfield"
      },
      "serviceSpecification": {"id": "fiber-internet-premium"}
    }
  }'
```

### **Enhanced Catalog APIs**
```bash
# Service Specifications (with filtering)
curl "http://localhost:8080/api/service-specifications?service_type=fiber_internet&limit=5"

# Product Offerings (with price filtering)
curl "http://localhost:8080/api/product-offerings?category=internet&min_price=50&max_price=100"

# Geographic Locations (with coverage)
curl "http://localhost:8080/api/geographic-locations?include_coverage=true&city=Springfield"

# Search functionality
curl "http://localhost:8080/api/service-specifications?search=fiber"
curl "http://localhost:8080/api/product-offerings?search=premium"
```

## 🛑 **Troubleshooting Guide**

### **Problem: Services Won't Start**

#### **Symptoms:**
- `docker-compose up -d` fails
- Containers exit immediately
- Connection refused errors

#### **Solutions:**
```bash
# Check Docker status
docker info

# Check for port conflicts
netstat -tulpn | grep :8080
netstat -tulpn | grep :5432

# Clean up Docker resources
docker-compose down -v
docker system prune -f
docker-compose up -d --build

# Check container logs
docker-compose logs catalog-manager
docker-compose logs postgres
```

### **Problem: Database Connection Errors**

#### **Symptoms:**
- "could not connect to server" errors
- Health check returns database disconnected
- API returns 500 errors

#### **Solutions:**
```bash
# Test database connectivity
docker-compose exec postgres pg_isready -U telecom_user

# Check database logs
docker-compose logs postgres

# Reset database
docker-compose down -v  # WARNING: This deletes data
docker-compose up -d

# Manual database connection test
docker-compose exec postgres psql -U telecom_user -d telecom_catalog -c "SELECT 1;"

# Check database credentials
docker-compose exec catalog-manager env | grep DB_
```

### **Problem: API Returns Errors**

#### **Symptoms:**
- 500 Internal Server Error
- 404 Not Found for valid endpoints
- Slow response times

#### **Solutions:**
```bash
# Check application logs
docker-compose logs -f catalog-manager

# Test health endpoint
curl -v http://localhost:8080/health

# Check if database is populated
docker-compose exec postgres psql -U telecom_user -d telecom_catalog -c "SELECT COUNT(*) FROM customers;"

# Restart catalog manager
docker-compose restart catalog-manager

# Check resource usage
docker stats
```

### **Problem: TMF622 Validation Errors**

#### **Symptoms:**
- "Input should be a valid dictionary" errors
- MCP tool validation failures
- List vs Dict type mismatches

#### **Solutions:**
```bash
# Verify API returns list format
curl -s "http://localhost:8080/tmf622/productOrder?limit=2" | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f'Type: {type(data)}')
print(f'Is list: {isinstance(data, list)}')
"

# Check MCP server configuration
cat ~/.config/claude_desktop/config.json

# Verify fixed MCP server is being used
ps aux | grep mcp_server_fixed.py

# Restart Claude Desktop after config changes
# (Kill Claude Desktop app and restart)
```

### **Problem: Claude Desktop MCP Connection Issues**

#### **Symptoms:**
- Tools not available in Claude Desktop
- MCP server connection failed
- "Tool not found" errors

#### **Solutions:**
```bash
# Check Claude Desktop configuration
cat ~/.config/claude_desktop/config.json

# Verify MCP server file exists and is executable
ls -la /path/to/mcp_server_fixed.py
chmod +x /path/to/mcp_server_fixed.py

# Test MCP server manually
cd /path/to/project
source venv/bin/activate
python mcp_server_fixed.py

# Check Python dependencies
pip list | grep mcp
pip list | grep aiohttp

# Restart Claude Desktop completely
# 1. Quit Claude Desktop (Cmd+Q)
# 2. Wait 5 seconds
# 3. Restart Claude Desktop
```

### **Problem: Performance Issues**

#### **Symptoms:**
- Slow API responses
- High CPU/Memory usage
- Database query timeouts

#### **Solutions:**
```bash
# Check resource usage
docker stats
htop  # or top

# Monitor database performance
docker-compose exec postgres psql -U telecom_user -d telecom_catalog -c "
SELECT query, calls, total_time, mean_time 
FROM pg_stat_statements 
ORDER BY total_time DESC 
LIMIT 10;"

# Check for long-running queries
docker-compose exec postgres psql -U telecom_user -d telecom_catalog -c "
SELECT pid, now() - pg_stat_activity.query_start AS duration, query 
FROM pg_stat_activity 
WHERE (now() - pg_stat_activity.query_start) > interval '5 minutes';"

# Optimize database
docker-compose exec postgres psql -U telecom_user -d telecom_catalog -c "VACUUM ANALYZE;"

# Scale resources (if needed)
# Edit docker-compose.yml to increase memory limits
```

### **Problem: Data Inconsistency**

#### **Symptoms:**
- Missing data in responses
- Broken relationships between entities
- Validation errors on valid data

#### **Solutions:**
```bash
# Check data integrity
docker-compose exec postgres psql -U telecom_user -d telecom_catalog -c "
SELECT 
  'customers' as table_name, COUNT(*) as count FROM customers
UNION ALL
SELECT 
  'orders' as table_name, COUNT(*) as count FROM orders
UNION ALL
SELECT 
  'service_specifications' as table_name, COUNT(*) as count FROM service_specifications;"

# Check for orphaned records
docker-compose exec postgres psql -U telecom_user -d telecom_catalog -c "
SELECT o.id, o.customer_id 
FROM orders o 
LEFT JOIN customers c ON o.customer_id = c.id 
WHERE c.id IS NULL;"

# Rebuild database (if necessary)
docker-compose down -v
docker-compose up -d
# Wait for initialization to complete
sleep 30
./scripts/validate_deployment.sh
```

## 📊 **Performance Monitoring**

### **Key Metrics to Monitor**
```bash
# API Response Time
curl -w "@curl-format.txt" -o /dev/null -s "http://localhost:8080/health"

# Database Connections
docker-compose exec postgres psql -U telecom_user -d telecom_catalog -c "
SELECT count(*) as connections, state 
FROM pg_stat_activity 
GROUP BY state;"

# Container Resource Usage
docker stats --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"

# Disk Usage
df -h
docker system df
```

### **Performance Thresholds**
- **API Response Time**: < 500ms for simple queries
- **Database Connections**: < 80% of max_connections
- **Memory Usage**: < 80% of available memory
- **CPU Usage**: < 70% sustained
- **Disk Usage**: < 85% full

## 🔧 **Emergency Procedures**

### **Service Recovery**
```bash
#!/bin/bash
# Emergency restart procedure

echo "🚨 Emergency service recovery started"

# Stop all services
docker-compose down

# Clean up resources
docker system prune -f

# Restart with fresh containers
docker-compose up -d --build

# Wait for services
sleep 30

# Validate system
if curl -sf http://localhost:8080/health > /dev/null; then
    echo "✅ Service recovery successful"
else
    echo "❌ Service recovery failed - manual intervention required"
fi
```

### **Data Recovery**
```bash
#!/bin/bash
# Emergency data recovery

BACKUP_DATE=$(date -d "yesterday" +%Y%m%d)

echo "🔄 Starting data recovery from $BACKUP_DATE"

# Stop services
docker-compose down

# Restore from backup
if [ -f "backups/$BACKUP_DATE/database.sql.gz" ]; then
    gunzip -c "backups/$BACKUP_DATE/database.sql.gz" | \
        docker-compose run --rm postgres psql -h postgres -U telecom_user telecom_catalog
    echo "✅ Database restored from $BACKUP_DATE"
else
    echo "❌ No backup found for $BACKUP_DATE"
fi

# Restart services
docker-compose up -d
```

## 📞 **Support Checklist**

When reporting issues, please provide:

### **System Information**
```bash
# Gather system information
echo "=== System Information ===" > support_info.txt
uname -a >> support_info.txt
docker --version >> support_info.txt
docker-compose --version >> support_info.txt
python3 --version >> support_info.txt

echo "=== Container Status ===" >> support_info.txt
docker-compose ps >> support_info.txt

echo "=== Recent Logs ===" >> support_info.txt
docker-compose logs --tail=50 >> support_info.txt

echo "=== Health Check ===" >> support_info.txt
curl -s http://localhost:8080/health >> support_info.txt

echo "=== Database Status ===" >> support_info.txt
docker-compose exec postgres pg_isready -U telecom_user >> support_info.txt 2>&1
```

### **Configuration Files**
- `docker-compose.yml` or `docker-compose.extended.yml`
- `~/.config/claude_desktop/config.json`
- Application logs from `docker-compose logs`

### **Error Messages**
- Exact error messages
- When the error first occurred
- Steps to reproduce the issue

---

## 🎯 **Quick Success Validation**

Run this command to verify everything is working:

```bash
#!/bin/bash
echo "🧪 Quick System Validation"
echo "========================="

# 1. Health check
if curl -sf http://localhost:8080/health > /dev/null; then
    echo "✅ System health: OK"
else
    echo "❌ System health: FAILED"
    exit 1
fi

# 2. TMF622 list format
if curl -sf "http://localhost:8080/tmf622/productOrder?limit=1" | python3 -c "import sys,json; assert isinstance(json.load(sys.stdin), list)" 2>/dev/null; then
    echo "✅ TMF622 list format: OK"
else
    echo "❌ TMF622 list format: FAILED"
fi

# 3. Enhanced APIs
if curl -sf "http://localhost:8080/api/service-specifications?limit=1" | python3 -c "import sys,json; assert len(json.load(sys.stdin)) > 0" 2>/dev/null; then
    echo "✅ Enhanced APIs: OK"
else
    echo "❌ Enhanced APIs: FAILED"
fi

echo "🎉 Validation complete!"
```

**If all checks pass, your Enhanced Catalog Manager is ready for production use!** 🚀