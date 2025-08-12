#!/bin/bash

# 🔧 Quick Fix for macOS psycopg2 Error
# Run this script to fix the pg_config error immediately

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}🔧 Fixing macOS psycopg2 Error...${NC}"

# Navigate to project directory
cd /Users/joe/dev/mcp_cm_v1

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo -e "${YELLOW}→ Activating virtual environment...${NC}"
    source venv/bin/activate
else
    echo -e "${YELLOW}→ Creating virtual environment...${NC}"
    python3 -m venv venv
    source venv/bin/activate
fi

# Upgrade pip
echo -e "${YELLOW}→ Upgrading pip...${NC}"
pip install --upgrade pip

# Remove any problematic psycopg2 installations
echo -e "${YELLOW}→ Removing problematic psycopg2 installations...${NC}"
pip uninstall psycopg2 psycopg2-binary -y 2>/dev/null || true

# Install PostgreSQL tools if needed (optional but helpful)
if ! command -v brew &> /dev/null; then
    echo -e "${YELLOW}→ Homebrew not found. Installing...${NC}"
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

# Install core dependencies
echo -e "${YELLOW}→ Installing core macOS dependencies...${NC}"
brew install python@3.11 docker git curl jq 2>/dev/null || true

# Install Python dependencies with binary packages
echo -e "${YELLOW}→ Installing Python dependencies (macOS optimized)...${NC}"

# Install psycopg2-binary first
pip install psycopg2-binary==2.9.7

# Install other core dependencies
pip install Flask>=3.0.0
pip install aiohttp>=3.9.0
pip install "mcp[fastmcp]>=1.0.0"
pip install python-dotenv>=1.0.0
pip install requests>=2.31.0

# Install additional dependencies from your requirements files
pip install -r requirements_catalog.txt
pip install -r requirements_mcp.txt

# Test the installation
echo -e "${YELLOW}→ Testing installation...${NC}"
python3 -c "
try:
    import psycopg2
    print('✅ psycopg2 working!')
    import flask
    print('✅ Flask working!')
    import aiohttp
    print('✅ aiohttp working!')
    import mcp
    print('✅ MCP working!')
    print('🎉 All dependencies installed successfully!')
except Exception as e:
    print(f'❌ Error: {e}')
    exit(1)
"

echo -e "${GREEN}✅ macOS setup fix completed successfully!${NC}"
echo ""
echo "🚀 Next steps:"
echo "1. Continue with your setup: ./setup_enhanced_catalog.sh"
echo "2. Or start Docker containers: docker-compose -f docker-compose.extended.yml up -d"
echo "3. Test the system: python test_complete_fixes.py"
echo ""
echo -e "${GREEN}🏆 Your Enhanced Catalog Manager is ready!${NC}"
