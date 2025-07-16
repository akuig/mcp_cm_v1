#!/bin/bash

echo "🔧 Quick Fix: Removing problematic packages and redeploying..."

# Stop containers and clean build cache
docker-compose down --remove-orphans
docker system prune -f
docker-compose down --rmi local

echo "✅ Cleaned up failed builds"
echo "🚀 Starting fresh deployment..."

# Redeploy with fixed requirements
./deploy.sh deploy