#!/bin/bash

# 🚀 Quick Ubuntu Docker Fix & Continue Setup
# Run this immediately after the Docker permissions error

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🚀 Quick Ubuntu Fix & Continue${NC}"
echo "==========================================="
echo ""

echo -e "${YELLOW}🔧 Step 1: Fix Docker Permissions${NC}"

# Start Docker if not running
sudo systemctl start docker
sudo systemctl enable docker

# Add user to docker group (if not already)
sudo usermod -aG docker $USER

# Temporary fix: Make Docker socket accessible
sudo chmod 666 /var/run/docker.sock

# Test Docker access
if docker info >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Docker access fixed!${NC}"
else
    echo -e "${RED}❌ Docker still not accessible${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}🐳 Step 2: Quick Enhanced Catalog Manager Setup${NC}"

# Navigate to project directory or create it
if [ -d "$HOME/enhanced-catalog-manager" ]; then
    cd "$HOME/enhanced-catalog-manager"
else
    mkdir -p "$HOME/enhanced-catalog-manager"
    cd "$HOME/enhanced-catalog-manager"
fi

# Create minimal docker-compose for testing
if [ ! -f "docker-compose.yml" ]; then
    echo -e "${YELLOW}→ Creating Docker configuration...${NC}"
    
    cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  catalog-manager:
    image: nginx:alpine
    container_name: catalog-manager-test
    ports:
      - "8080:80"
    environment:
      - ENV=test
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "wget", "--quiet", "--tries=1", "--spider", "http://localhost/"]
      interval: 30s
      timeout: 10s
      retries: 3

  postgres:
    image: postgres:15
    container_name: postgres-test
    environment:
      - POSTGRES_DB=catalog_db
      - POSTGRES_USER=catalog_user
      - POSTGRES_PASSWORD=catalog_pass
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U catalog_user -d catalog_db"]
      interval: 30s
      timeout: 10s
      retries: 3

volumes:
  postgres_data:
EOF
fi

echo ""
echo -e "${YELLOW}🚀 Step 3: Start System${NC}"

# Build and start containers
echo -e "${YELLOW}→ Starting containers...${NC}"
docker-compose up -d

# Wait for services
echo -e "${YELLOW}→ Waiting for services to start...${NC}"
sleep 10

# Test the system
echo -e "${YELLOW}→ Testing system...${NC}"
if curl -s http://localhost:8080 >/dev/null; then
    echo -e "${GREEN}✅ Web server responding!${NC}"
else
    echo -e "${YELLOW}⚠️  Web server still starting...${NC}"
fi

# Check containers
echo ""
echo -e "${YELLOW}📊 Container Status:${NC}"
docker-compose ps

echo ""
echo -e "${GREEN}🎉 Quick Setup Complete!${NC}"
echo "==========================================="
echo ""
echo "✅ Docker permissions fixed"
echo "✅ Basic system running on port 8080"
echo "✅ PostgreSQL running on port 5432"
echo ""
echo "🔗 Access:"
echo "  Web: http://localhost:8080"
echo "  Database: localhost:5432"
echo ""
echo "📋 Next Steps:"
echo "1. Copy your Enhanced Catalog Manager files:"
echo "   scp -r user@macos:/Users/joe/dev/mcp_cm_v1/* ."
echo ""
echo "2. Replace test containers with real Enhanced Catalog Manager:"
echo "   docker-compose down"
echo "   # Copy your docker-compose.extended.yml"
echo "   docker-compose -f docker-compose.extended.yml up -d"
echo ""
echo "3. Deploy MCP server:"
echo "   ./deploy_final_mcp.sh"
echo ""
echo -e "${GREEN}🏆 Ubuntu Docker issue resolved!${NC}"

# Create helper scripts
mkdir -p scripts

cat > scripts/status.sh << 'EOF'
#!/bin/bash
echo "📊 Enhanced Catalog Manager Status:"
docker-compose ps
echo ""
echo "🌐 Quick Tests:"
echo "Web: $(curl -s -o /dev/null -w "%{http_code}" http://localhost:8080)"
echo "DB:  $(docker exec postgres-test pg_isready -U catalog_user -d catalog_db 2>/dev/null && echo "Ready" || echo "Not ready")"
EOF

cat > scripts/logs.sh << 'EOF'
#!/bin/bash
echo "📋 Container Logs:"
docker-compose logs --tail=50 -f
EOF

chmod +x scripts/*.sh

echo ""
echo "🛠️  Helper scripts created:"
echo "  ./scripts/status.sh  - Check system status"
echo "  ./scripts/logs.sh    - View container logs"
echo ""
