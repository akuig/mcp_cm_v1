#!/bin/bash

# Quick fix script for deployment issues
echo "🔧 Fixing deployment issues..."

# Stop any running containers
docker-compose down --remove-orphans 2>/dev/null || true

# Remove any failed build containers
docker system prune -f

# Remove old images to force rebuild
docker-compose down --rmi local 2>/dev/null || true

echo "✅ Cleanup completed"
echo "🚀 Ready to redeploy with fixed requirements"
echo ""
echo "Run: ./deploy.sh deploy"