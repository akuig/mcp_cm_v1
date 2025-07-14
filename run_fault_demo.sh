#!/bin/bash
# Simple script to run the fault management demo

echo "🚀 Starting Fault Management Demo..."
echo ""

# Step 1: Check if docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Step 2: Stop any existing services
echo "📦 Stopping any existing services..."
docker-compose -f docker-compose-with-fault.yml down > /dev/null 2>&1

# Step 3: Start services
echo "🔧 Starting services with fault management..."
docker-compose -f docker-compose-with-fault.yml up -d

# Step 4: Wait for services to be ready
echo "⏳ Waiting for services to initialize (20 seconds)..."
sleep 20

# Step 5: Check if services are healthy
echo "🔍 Checking service health..."
python3 check_services.py

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Services failed to start properly."
    echo "Check logs with: docker-compose -f docker-compose-with-fault.yml logs"
    exit 1
fi

# Step 6: Run the demo
echo ""
echo "🎯 Running fault management demo..."
echo ""
python3 test_fault_management.py
