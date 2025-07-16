#!/bin/bash

echo "🔧 Fixing web-ui container issue..."

# Remove the failed web-ui container
docker-compose rm -f web-ui 2>/dev/null || true

# Start the web-ui container with fixed configuration
docker-compose up -d web-ui

echo "✅ Web UI container restarted"
echo "🌐 Testing web interface..."

# Wait a moment for container to start
sleep 3

# Test if web UI is accessible
if curl -f http://localhost:8082 &>/dev/null; then
    echo "✅ Web UI is accessible at http://localhost:8082"
else
    echo "⚠️  Web UI may still be starting up. Try http://localhost:8082 in a moment."
fi

echo ""
echo "🎉 SYSTEM STATUS CHECK:"
echo "========================"
docker-compose ps