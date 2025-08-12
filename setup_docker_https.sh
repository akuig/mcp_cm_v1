#!/bin/bash

# 🐳 Docker HTTPS Setup for Enhanced Catalog Manager
# Adds HTTPS support using nginx container

set -e

echo "🐳 Docker HTTPS Setup"
echo "===================="
echo ""

# Create nginx directory structure
echo "→ Creating nginx configuration..."
mkdir -p nginx/ssl

# Generate SSL certificate
echo "→ Generating SSL certificate..."
openssl req -x509 -newkey rsa:2048 -keyout nginx/ssl/key.pem -out nginx/ssl/cert.pem -days 365 -nodes \
    -subj "/C=US/ST=State/L=City/O=EnhancedCatalogManager/CN=localhost"

# Create nginx configuration
echo "→ Creating nginx configuration..."
cat > nginx/nginx.conf << 'EOF'
events {
    worker_connections 1024;
}

http {
    # Basic settings
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;

    # MIME types
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # SSL Settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # HTTP to HTTPS redirect
    server {
        listen 80;
        server_name localhost;
        return 301 https://$host$request_uri;
    }

    # HTTPS server
    server {
        listen 443 ssl;
        server_name localhost;

        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;

        # Proxy to catalog-manager
        location / {
            proxy_pass http://catalog-manager:8080;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto https;
            proxy_set_header X-Forwarded-Ssl on;
            
            # WebSocket support (if needed)
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
        }

        # Health check endpoint
        location /health {
            proxy_pass http://catalog-manager:8080/health;
            proxy_set_header Host $host;
        }
    }
}
EOF

echo "✅ nginx configuration created"

# Stop existing containers
echo "→ Stopping existing containers..."
docker-compose down 2>/dev/null || true

# Start with HTTPS support
echo "→ Starting containers with HTTPS support..."
docker-compose -f docker-compose.https.yml up -d

# Wait for services
echo "→ Waiting for services to start..."
sleep 10

# Test the setup
echo "🧪 Testing HTTPS setup..."

# Test HTTP redirect
echo "→ Testing HTTP redirect..."
if curl -s -o /dev/null -w "%{http_code}" http://localhost | grep -q "301"; then
    echo "✅ HTTP redirects to HTTPS"
else
    echo "⚠️  HTTP redirect may not be working"
fi

# Test HTTPS
echo "→ Testing HTTPS endpoint..."
if curl -k -s https://localhost/health >/dev/null; then
    echo "✅ HTTPS endpoint working!"
    echo ""
    echo "🎉 Docker HTTPS Setup Complete!"
    echo ""
    echo "📡 Access URLs:"
    echo "  HTTPS: https://localhost      (Claude Desktop)"
    echo "  HTTP:  http://localhost:8080  (Direct access - MCP Inspector)"
    echo ""
    echo "🔧 Container Status:"
    docker-compose -f docker-compose.https.yml ps
    echo ""
    echo "🧪 Quick Test:"
    curl -k -s https://localhost/health | jq '.' 2>/dev/null || curl -k -s https://localhost/health
else
    echo "❌ HTTPS endpoint failed"
    echo ""
    echo "🔍 Troubleshooting:"
    echo "  Logs: docker-compose -f docker-compose.https.yml logs"
    echo "  Status: docker-compose -f docker-compose.https.yml ps"
fi

echo ""
echo "📋 Next Steps:"
echo "1. Configure Claude Desktop to use: https://localhost"
echo "2. Accept the self-signed certificate warning"
echo "3. Test all 13 Enhanced Catalog Manager tools"
echo ""
