#!/bin/bash

# 🔧 Ubuntu Docker Permissions Fix
# Fixes the common "Permission denied" Docker error on fresh Ubuntu installs

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🔧 Ubuntu Docker Permissions Fix${NC}"
echo "==========================================="
echo ""

# Check current Docker access
echo -e "${YELLOW}🔍 Diagnosing Docker permissions...${NC}"

# Check if Docker daemon is running
if ! sudo systemctl is-active --quiet docker; then
    echo -e "${YELLOW}→ Starting Docker daemon...${NC}"
    sudo systemctl start docker
    sudo systemctl enable docker
fi

# Check if user is in docker group
if groups | grep -q docker; then
    echo -e "${GREEN}✅ User $(whoami) is in docker group${NC}"
else
    echo -e "${YELLOW}→ Adding user $(whoami) to docker group...${NC}"
    sudo usermod -aG docker $USER
fi

# Check Docker socket permissions
echo -e "${YELLOW}→ Checking Docker socket permissions...${NC}"
ls -la /var/run/docker.sock

# Try Docker command
echo -e "${YELLOW}→ Testing Docker access...${NC}"
if docker info >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Docker access working!${NC}"
else
    echo -e "${RED}❌ Docker access still blocked${NC}"
    echo ""
    echo -e "${YELLOW}🔧 Applying fixes...${NC}"
    
    # Ensure Docker daemon is running
    sudo systemctl restart docker
    
    # Fix socket permissions (temporary)
    sudo chmod 666 /var/run/docker.sock
    
    # Verify fix
    if docker info >/dev/null 2>&1; then
        echo -e "${GREEN}✅ Docker access fixed temporarily!${NC}"
        echo ""
        echo -e "${YELLOW}⚠️  For permanent fix, please:${NC}"
        echo "   1. Log out of Ubuntu completely"
        echo "   2. Log back in"
        echo "   3. Run the setup script again"
        echo ""
        echo -e "${BLUE}Or continue with the temporary fix right now...${NC}"
    else
        echo -e "${RED}❌ Could not fix Docker permissions${NC}"
        exit 1
    fi
fi

echo ""
echo -e "${GREEN}🚀 Docker is now accessible!${NC}"
echo ""
echo "Next steps:"
echo "1. Continue with Enhanced Catalog Manager setup"
echo "2. Or run: docker-compose -f docker-compose.extended.yml up -d"
echo ""

# Test Docker Compose
echo -e "${YELLOW}🧪 Testing Docker Compose...${NC}"
if docker-compose --version >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Docker Compose working: $(docker-compose --version)${NC}"
else
    echo -e "${YELLOW}→ Installing Docker Compose...${NC}"
    sudo apt update
    sudo apt install -y docker-compose
fi

echo ""
echo -e "${GREEN}🎉 Docker permissions fixed! Setup can continue.${NC}"
