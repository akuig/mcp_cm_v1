# Quick Start Instructions for Fault Management Demo

## Prerequisites
Make sure you have Docker and Docker Compose installed.

## Step 1: Stop any existing services
```bash
docker-compose down
docker-compose -f docker-compose-with-fault.yml down
```

## Step 2: Start services with fault management
```bash
docker-compose -f docker-compose-with-fault.yml up -d
```

## Step 3: Wait for services to start (important!)
```bash
# Wait about 15-20 seconds for all services to initialize
sleep 20

# Or check service status:
python check_services.py
```

## Step 4: Run the fault management demo
```bash
python test_fault_management.py
```

## Troubleshooting

### If services aren't running:
```bash
# Check logs
docker-compose -f docker-compose-with-fault.yml logs

# Check specific service
docker-compose -f docker-compose-with-fault.yml logs fault-manager
```

### If ports are in use:
```bash
# Stop all services and remove containers
docker-compose -f docker-compose-with-fault.yml down
docker container prune -f
```

### To reset everything:
```bash
docker-compose -f docker-compose-with-fault.yml down -v
docker-compose -f docker-compose-with-fault.yml up -d
```

## What the demo shows:
1. Customer (Jane Doe) calls about internet outage
2. Agent detects fiber cut on Main Street
3. Traffic is rerouted (15-min temporary fix)
4. Technician is dispatched (4-hour permanent fix)  
5. Trouble ticket created and SMS sent
6. Service restored to normal

## Key files:
- `docker-compose-with-fault.yml` - Docker setup with fault manager
- `fault_manager.py` - Fault management service
- `test_fault_management.py` - Demo script
- `check_services.py` - Service status checker
