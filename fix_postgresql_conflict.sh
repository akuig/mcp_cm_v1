#!/bin/bash

# 🔧 Ubuntu PostgreSQL Port Conflict Fix
# Resolves Docker PostgreSQL conflict with system PostgreSQL

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🔧 PostgreSQL Port Conflict Fix${NC}"
echo "==========================================="
echo ""

# Check what's using port 5432
echo -e "${YELLOW}🔍 Checking port 5432 usage...${NC}"
if lsof -i :5432 >/dev/null 2>&1; then
    echo -e "${RED}❌ Port 5432 is in use:${NC}"
    lsof -i :5432
    echo ""
else
    echo -e "${GREEN}✅ Port 5432 is free${NC}"
    exit 0
fi

# Check if system PostgreSQL is running
if systemctl is-active --quiet postgresql; then
    echo -e "${YELLOW}📊 System PostgreSQL Status:${NC}"
    systemctl status postgresql --no-pager -l
    echo ""
fi

echo -e "${BLUE}Choose your fix:${NC}"
echo ""
echo "1. 🛑 Stop system PostgreSQL (use Docker PostgreSQL)"
echo "2. 🐳 Change Docker PostgreSQL port (keep both running)"  
echo "3. 🔄 Use system PostgreSQL (skip Docker PostgreSQL)"
echo "4. 📊 Just show status and exit"
echo ""
read -p "Enter choice (1-4): " choice

case $choice in
    1)
        echo -e "${YELLOW}🛑 Stopping system PostgreSQL...${NC}"
        sudo systemctl stop postgresql
        sudo systemctl disable postgresql
        echo -e "${GREEN}✅ System PostgreSQL stopped${NC}"
        echo "Now you can start Docker containers:"
        echo "  docker-compose up -d"
        ;;
    2)
        echo -e "${YELLOW}🐳 Creating Docker config with different port...${NC}"
        
        # Backup original docker-compose
        if [ -f "docker-compose.yml" ]; then
            cp docker-compose.yml docker-compose.yml.backup
        fi
        
        # Update PostgreSQL port in docker-compose
        if [ -f "docker-compose.yml" ]; then
            sed -i 's/5432:5432/5433:5432/g' docker-compose.yml
            echo -e "${GREEN}✅ Updated Docker PostgreSQL port to 5433${NC}"
        fi
        
        if [ -f "docker-compose.extended.yml" ]; then
            sed -i 's/5432:5432/5433:5432/g' docker-compose.extended.yml
            echo -e "${GREEN}✅ Updated Extended Docker PostgreSQL port to 5433${NC}"
        fi
        
        echo ""
        echo -e "${GREEN}✅ Port configuration updated${NC}"
        echo "System PostgreSQL: localhost:5432"
        echo "Docker PostgreSQL: localhost:5433"
        echo ""
        echo "Start containers with:"
        echo "  docker-compose up -d"
        ;;
    3)
        echo -e "${YELLOW}🔄 Configuring to use system PostgreSQL...${NC}"
        
        # Create database and user if they don't exist
        sudo -u postgres psql -c "CREATE DATABASE catalog_db;" 2>/dev/null || echo "Database catalog_db already exists"
        sudo -u postgres psql -c "CREATE USER catalog_user WITH PASSWORD 'catalog_pass';" 2>/dev/null || echo "User catalog_user already exists"
        sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE catalog_db TO catalog_user;" 2>/dev/null || echo "Privileges already granted"
        
        # Remove PostgreSQL service from docker-compose
        if [ -f "docker-compose.yml" ]; then
            # Create version without PostgreSQL service
            python3 -c "
import yaml
with open('docker-compose.yml', 'r') as f:
    config = yaml.safe_load(f)
if 'services' in config and 'postgres' in config['services']:
    del config['services']['postgres']
    # Update database URL for catalog-manager
    if 'catalog-manager' in config['services']:
        env = config['services']['catalog-manager'].get('environment', [])
        for i, var in enumerate(env):
            if var.startswith('DATABASE_URL'):
                env[i] = 'DATABASE_URL=postgresql://catalog_user:catalog_pass@host.docker.internal:5432/catalog_db'
        config['services']['catalog-manager']['environment'] = env
with open('docker-compose.yml', 'w') as f:
    yaml.dump(config, f)
print('✅ Updated docker-compose.yml to use system PostgreSQL')
" 2>/dev/null || echo "Manually edit docker-compose.yml to remove postgres service"
        fi
        
        echo -e "${GREEN}✅ Configured to use system PostgreSQL${NC}"
        echo "Database: postgresql://catalog_user:catalog_pass@localhost:5432/catalog_db"
        ;;
    4)
        echo -e "${YELLOW}📊 Current Status:${NC}"
        echo ""
        echo "System Services:"
        systemctl is-active postgresql && echo "  PostgreSQL: Running on port 5432" || echo "  PostgreSQL: Stopped"
        echo ""
        echo "Docker Containers:"
        docker-compose ps 2>/dev/null || echo "  No containers running"
        echo ""
        echo "Port Usage:"
        lsof -i :5432 2>/dev/null || echo "  Port 5432: Free"
        lsof -i :5433 2>/dev/null || echo "  Port 5433: Free"
        ;;
    *)
        echo -e "${RED}❌ Invalid choice${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}🎉 PostgreSQL conflict resolution complete!${NC}"
echo ""
echo "Next steps:"
echo "  1. Start Docker containers: docker-compose up -d"
echo "  2. Test the system: curl http://localhost:8080/health"
echo "  3. Check status: docker-compose ps"
echo ""
