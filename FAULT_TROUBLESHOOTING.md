# Fault Management Demo Troubleshooting

## Common Issues and Solutions

### 1. "JSONDecodeError: Expecting value"
**Cause**: Services are not running or not responding properly.

**Solution**:
```bash
# Check if services are running
python check_services.py

# If not, start them:
docker-compose -f docker-compose-with-fault.yml up -d

# Wait for initialization
sleep 20
```

### 2. "Connection refused" errors
**Cause**: Services haven't finished starting.

**Solution**:
```bash
# Wait longer for services to start
sleep 30

# Check Docker logs
docker-compose -f docker-compose-with-fault.yml logs fault-manager
```

### 3. Port already in use
**Cause**: Another service is using ports 8080, 8081, or 8090.

**Solution**:
```bash
# Stop all containers
docker-compose -f docker-compose-with-fault.yml down
docker container prune -f

# Check what's using the ports
lsof -i :8080
lsof -i :8081
lsof -i :8090
```

### 4. Fault Manager not starting
**Cause**: Missing dependencies or configuration issues.

**Solution**:
```bash
# Rebuild the image
docker-compose -f docker-compose-with-fault.yml build fault-manager

# Check logs
docker-compose -f docker-compose-with-fault.yml logs fault-manager
```

### 5. Database connection errors
**Cause**: PostgreSQL not ready or initialized.

**Solution**:
```bash
# Reset everything
docker-compose -f docker-compose-with-fault.yml down -v
docker-compose -f docker-compose-with-fault.yml up -d
```

## Quick Diagnostic Commands

```bash
# Check all service status
docker-compose -f docker-compose-with-fault.yml ps

# View all logs
docker-compose -f docker-compose-with-fault.yml logs

# Test Fault Manager directly
curl -X POST http://localhost:8081/serviceStatus/check \
  -H "Content-Type: application/json" \
  -d '{"location": {"streetName": "Main Street", "city": "Dublin"}}'

# Check if fault simulation is active
curl http://localhost:8081/docs
```

## Complete Reset

If nothing works, do a complete reset:

```bash
# Stop everything
docker-compose -f docker-compose-with-fault.yml down -v

# Remove all containers and images
docker container prune -f
docker image prune -f

# Rebuild and start
docker-compose -f docker-compose-with-fault.yml build
docker-compose -f docker-compose-with-fault.yml up -d

# Wait for services
sleep 30

# Run demo
python test_fault_management.py
```

## Using the Automated Script

The easiest way to run the demo:

```bash
chmod +x run_fault_demo.sh
./run_fault_demo.sh
```

This script handles all the startup and checks automatically.
