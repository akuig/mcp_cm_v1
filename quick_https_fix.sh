#!/bin/bash

# 🚀 Quick HTTPS Fix for Claude Desktop
# Immediate SSL setup using nginx reverse proxy

set -e

echo "🔒 Quick HTTPS Setup for Claude Desktop"
echo "======================================="
echo ""

# Install nginx
echo "→ Installing nginx..."
sudo apt update
sudo apt install -y nginx openssl

# Create SSL certificate
echo "→ Creating SSL certificate..."
sudo mkdir -p /etc/nginx/ssl
sudo openssl req -x509 -newkey rsa:2048 -keyout /etc/nginx/ssl/key.pem -out /etc/nginx/ssl/cert.pem -days 365 -nodes \
    -subj "/C=US/ST=State/L=City/O=EnhancedCatalogManager/CN=localhost"

# Create nginx configuration
echo "→ Configuring nginx reverse proxy..."
sudo tee /etc/nginx/sites-available/https-proxy << 'EOF'
server {
    listen 443 ssl;
    server_name localhost;
    
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    
    # SSL settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    
    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
    }
}

server {
    listen 80;
    server_name localhost;
    return 301 https://$host$request_uri;
}
EOF

# Enable the configuration
sudo ln -sf /etc/nginx/sites-available/https-proxy /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test and start nginx
sudo nginx -t
sudo systemctl restart nginx
sudo systemctl enable nginx

echo ""
echo "✅ HTTPS Setup Complete!"
echo ""
echo "📡 Your Enhanced Catalog Manager is now available on:"
echo "  HTTP:  http://localhost:8080  (Direct - MCP Inspector)"
echo "  HTTPS: https://localhost      (nginx proxy - Claude Desktop)"
echo ""
echo "🧪 Test the setup:"
echo "  curl http://localhost:8080/health   # Direct HTTP"
echo "  curl -k https://localhost/health    # HTTPS via nginx"
echo ""
echo "🔧 Claude Desktop Configuration:"
echo '  Use: "https://localhost" as your MCP server URL'
echo "  Note: You'll need to accept the self-signed certificate"
echo ""

# Test the setup
echo "🧪 Testing HTTPS endpoint..."
sleep 2
if curl -k -s https://localhost/health >/dev/null; then
    echo "✅ HTTPS endpoint working!"
    echo ""
    echo "🎉 Ready for Claude Desktop connection!"
    echo "   URL: https://localhost"
else
    echo "❌ HTTPS endpoint test failed"
    echo "Check nginx status: sudo systemctl status nginx"
fi
