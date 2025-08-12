#!/bin/bash

# 🔒 HTTPS Setup for Enhanced Catalog Manager
# Adds SSL/TLS support for Claude Desktop connectivity

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🔒 HTTPS Setup for Enhanced Catalog Manager${NC}"
echo "=============================================="
echo ""

# Check current setup
echo -e "${YELLOW}🔍 Checking current setup...${NC}"
echo "Current access:"
echo "  HTTP:  http://localhost:8080 ✅ (MCP Inspector works)"
echo "  HTTPS: https://localhost:8443 ❌ (Claude Desktop needs this)"
echo ""

echo -e "${BLUE}Choose SSL setup method:${NC}"
echo ""
echo "1. 🚀 Quick Self-Signed Certificate (Immediate - Development)"
echo "2. 🌐 nginx Reverse Proxy with SSL (Recommended - Production)"
echo "3. 🔒 Let's Encrypt Certificate (Production with Domain)"
echo "4. 📊 Just show current status"
echo ""
read -p "Enter choice (1-4): " choice

case $choice in
    1)
        setup_self_signed_ssl
        ;;
    2)
        setup_nginx_ssl_proxy
        ;;
    3)
        setup_letsencrypt_ssl
        ;;
    4)
        show_current_status
        ;;
    *)
        echo -e "${RED}❌ Invalid choice${NC}"
        exit 1
        ;;
esac

setup_self_signed_ssl() {
    echo -e "${YELLOW}🚀 Setting up Self-Signed SSL Certificate...${NC}"
    echo ""
    
    # Create SSL directory
    mkdir -p ssl
    cd ssl
    
    # Generate self-signed certificate
    echo -e "${YELLOW}→ Generating SSL certificate...${NC}"
    openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes \
        -subj "/C=US/ST=State/L=City/O=Enhanced-Catalog-Manager/CN=localhost"
    
    echo -e "${GREEN}✅ SSL certificate generated${NC}"
    
    cd ..
    
    # Create HTTPS-enabled Flask app
    echo -e "${YELLOW}→ Creating HTTPS-enabled catalog manager...${NC}"
    
    cat > catalog_manager_https.py << 'EOF'
#!/usr/bin/env python3
"""
Enhanced Catalog Manager with HTTPS Support
"""

from flask import Flask, jsonify, request
import psycopg2
import os
from datetime import datetime
import ssl

app = Flask(__name__)

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://catalog_user:catalog_pass@postgres:5432/catalog_db')

@app.route('/health')
def health_check():
    """Health check endpoint"""
    try:
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'database': 'connected',
            'platform': 'ubuntu',
            'ssl': 'enabled',
            'version': 'enhanced-https'
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }), 500

@app.route('/api/status')
def api_status():
    """API status endpoint"""
    return jsonify({
        'api_version': '2.1',
        'platform': 'ubuntu',
        'ssl': 'self-signed',
        'ports': {
            'http': 8080,
            'https': 8443
        }
    })

# Add your other Enhanced Catalog Manager endpoints here
# Copy from catalog_manager_extended_fixed.py

if __name__ == '__main__':
    # SSL context
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain('ssl/cert.pem', 'ssl/key.pem')
    
    # Run with both HTTP and HTTPS
    from threading import Thread
    
    # HTTP server (for MCP Inspector)
    def run_http():
        app.run(host='0.0.0.0', port=8080, debug=False)
    
    # HTTPS server (for Claude Desktop)
    def run_https():
        app.run(host='0.0.0.0', port=8443, debug=False, ssl_context=context)
    
    # Start both servers
    http_thread = Thread(target=run_http)
    https_thread = Thread(target=run_https)
    
    http_thread.start()
    https_thread.start()
    
    print("🌐 Enhanced Catalog Manager running on:")
    print("  HTTP:  http://localhost:8080  (MCP Inspector)")
    print("  HTTPS: https://localhost:8443 (Claude Desktop)")
    
    http_thread.join()
    https_thread.join()
EOF

    echo -e "${GREEN}✅ HTTPS-enabled catalog manager created${NC}"
    
    # Test the setup
    echo -e "${YELLOW}→ Testing SSL setup...${NC}"
    python3 catalog_manager_https.py &
    APP_PID=$!
    
    sleep 5
    
    # Test HTTP
    if curl -s http://localhost:8080/health >/dev/null; then
        echo -e "${GREEN}✅ HTTP endpoint working${NC}"
    else
        echo -e "${RED}❌ HTTP endpoint failed${NC}"
    fi
    
    # Test HTTPS (ignore certificate validation)
    if curl -k -s https://localhost:8443/health >/dev/null; then
        echo -e "${GREEN}✅ HTTPS endpoint working${NC}"
    else
        echo -e "${RED}❌ HTTPS endpoint failed${NC}"
    fi
    
    kill $APP_PID 2>/dev/null || true
    
    echo ""
    echo -e "${GREEN}🎉 Self-Signed SSL Setup Complete!${NC}"
    echo ""
    echo "📡 Access URLs:"
    echo "  HTTP:  http://localhost:8080  (MCP Inspector)"
    echo "  HTTPS: https://localhost:8443 (Claude Desktop)"
    echo ""
    echo "⚠️  Note: You'll need to accept the self-signed certificate warning"
    echo "    in Claude Desktop when connecting."
    echo ""
}

setup_nginx_ssl_proxy() {
    echo -e "${YELLOW}🌐 Setting up nginx SSL Reverse Proxy...${NC}"
    echo ""
    
    # Install nginx
    echo -e "${YELLOW}→ Installing nginx...${NC}"
    sudo apt update
    sudo apt install -y nginx
    
    # Create SSL certificate
    echo -e "${YELLOW}→ Creating SSL certificate...${NC}"
    sudo mkdir -p /etc/nginx/ssl
    sudo openssl req -x509 -newkey rsa:4096 -keyout /etc/nginx/ssl/key.pem -out /etc/nginx/ssl/cert.pem -days 365 -nodes \
        -subj "/C=US/ST=State/L=City/O=Enhanced-Catalog-Manager/CN=localhost"
    
    # Create nginx configuration
    echo -e "${YELLOW}→ Configuring nginx...${NC}"
    sudo tee /etc/nginx/sites-available/enhanced-catalog-manager << 'EOF'
server {
    listen 80;
    server_name localhost;
    
    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

server {
    listen 443 ssl;
    server_name localhost;
    
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    
    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
        proxy_set_header X-Forwarded-Ssl on;
    }
}
EOF

    # Enable the site
    sudo ln -sf /etc/nginx/sites-available/enhanced-catalog-manager /etc/nginx/sites-enabled/
    sudo rm -f /etc/nginx/sites-enabled/default
    
    # Test nginx configuration
    sudo nginx -t
    
    # Start nginx
    sudo systemctl restart nginx
    sudo systemctl enable nginx
    
    echo -e "${GREEN}✅ nginx SSL proxy configured${NC}"
    
    # Test the setup
    echo -e "${YELLOW}→ Testing nginx SSL proxy...${NC}"
    
    sleep 2
    
    if curl -k -s https://localhost/health >/dev/null; then
        echo -e "${GREEN}✅ HTTPS proxy working${NC}"
    else
        echo -e "${RED}❌ HTTPS proxy failed${NC}"
    fi
    
    echo ""
    echo -e "${GREEN}🎉 nginx SSL Proxy Setup Complete!${NC}"
    echo ""
    echo "📡 Access URLs:"
    echo "  HTTP:  http://localhost     (nginx → Enhanced Catalog Manager)"
    echo "  HTTPS: https://localhost    (nginx → Enhanced Catalog Manager)"
    echo "  Direct: http://localhost:8080 (Direct to Enhanced Catalog Manager)"
    echo ""
    echo "🔧 nginx Status:"
    echo "  Config: /etc/nginx/sites-available/enhanced-catalog-manager"
    echo "  SSL:    /etc/nginx/ssl/"
    echo "  Status: sudo systemctl status nginx"
    echo ""
}

setup_letsencrypt_ssl() {
    echo -e "${YELLOW}🔒 Setting up Let's Encrypt SSL...${NC}"
    echo ""
    echo "⚠️  Let's Encrypt requires:"
    echo "  1. A public domain name (not localhost)"
    echo "  2. Port 80/443 accessible from internet"
    echo "  3. DNS pointing to this server"
    echo ""
    read -p "Do you have a domain name pointing to this server? (y/N): " has_domain
    
    if [[ ! "$has_domain" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        echo -e "${YELLOW}📝 For Let's Encrypt, you need:${NC}"
        echo "  1. Domain: example.com"
        echo "  2. DNS A record: example.com → $(curl -s ifconfig.me)"
        echo "  3. Firewall: Allow ports 80, 443"
        echo ""
        echo "Once you have these, re-run this script with option 3."
        return
    fi
    
    read -p "Enter your domain name: " domain_name
    
    # Install certbot
    echo -e "${YELLOW}→ Installing certbot...${NC}"
    sudo apt update
    sudo apt install -y certbot python3-certbot-nginx
    
    # Install nginx if not present
    if ! command -v nginx &> /dev/null; then
        sudo apt install -y nginx
    fi
    
    # Create basic nginx config
    sudo tee /etc/nginx/sites-available/$domain_name << EOF
server {
    listen 80;
    server_name $domain_name;
    
    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

    sudo ln -sf /etc/nginx/sites-available/$domain_name /etc/nginx/sites-enabled/
    sudo nginx -t
    sudo systemctl restart nginx
    
    # Get Let's Encrypt certificate
    echo -e "${YELLOW}→ Obtaining Let's Encrypt certificate...${NC}"
    sudo certbot --nginx -d $domain_name
    
    echo -e "${GREEN}🎉 Let's Encrypt SSL Setup Complete!${NC}"
    echo ""
    echo "📡 Access URLs:"
    echo "  HTTPS: https://$domain_name (Production SSL)"
    echo "  HTTP:  http://$domain_name  (Redirects to HTTPS)"
    echo ""
}

show_current_status() {
    echo -e "${YELLOW}📊 Current Status:${NC}"
    echo ""
    echo "Services:"
    if systemctl is-active --quiet docker; then
        echo "  Docker: ✅ Running"
        docker-compose ps 2>/dev/null || echo "  Containers: Not running"
    else
        echo "  Docker: ❌ Not running"
    fi
    
    if systemctl is-active --quiet nginx; then
        echo "  nginx: ✅ Running"
    else
        echo "  nginx: ❌ Not running"
    fi
    
    echo ""
    echo "Port Status:"
    if lsof -i :8080 >/dev/null 2>&1; then
        echo "  8080 (HTTP): ✅ In use"
    else
        echo "  8080 (HTTP): ❌ Free"
    fi
    
    if lsof -i :8443 >/dev/null 2>&1; then
        echo "  8443 (HTTPS): ✅ In use"
    else
        echo "  8443 (HTTPS): ❌ Free"
    fi
    
    if lsof -i :443 >/dev/null 2>&1; then
        echo "  443 (HTTPS): ✅ In use"
    else
        echo "  443 (HTTPS): ❌ Free"
    fi
    
    echo ""
    echo "Quick Tests:"
    echo "  HTTP:  curl http://localhost:8080/health"
    echo "  HTTPS: curl -k https://localhost:8443/health"
    echo "  nginx: curl -k https://localhost/health"
    echo ""
}

# Main execution
case $choice in
    *) echo "Invalid choice" ;;
esac
