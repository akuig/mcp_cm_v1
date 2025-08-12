#!/usr/bin/env bash

# Script to apply enhanced updates to the MCP Catalog Manager project
# This will update your project to use the enhanced version with 13 tools

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_msg() {
    local color=$1
    local msg=$2
    echo -e "${color}${msg}${NC}"
}

# Check if we're in the right directory
if [ ! -f "catalog_manager_extended.py" ] || [ ! -f "mcp_fastmcp_server_extended.py" ]; then
    print_msg "$RED" "❌ Error: Required extended files not found!"
    print_msg "$YELLOW" "Please run this script from the /Users/joe/dev/mcp_cm_v1 directory"
    exit 1
fi

print_msg "$BLUE" "🔄 Applying Enhanced MCP Updates..."
print_msg "$BLUE" "===================================="

# Backup existing files
print_msg "$YELLOW" "📦 Creating backups..."
mkdir -p backups/$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"

# Backup current files if they exist
[ -f "Makefile" ] && cp Makefile "$BACKUP_DIR/"
[ -f "docker-compose.yml" ] && cp docker-compose.yml "$BACKUP_DIR/"
[ -f "Dockerfile.catalog.enhanced" ] && cp Dockerfile.catalog.enhanced "$BACKUP_DIR/"
[ -f "Dockerfile.mcp.enhanced" ] && cp Dockerfile.mcp.enhanced "$BACKUP_DIR/"

print_msg "$GREEN" "✅ Backups created in $BACKUP_DIR"

# Create new Dockerfile.catalog.enhanced
print_msg "$YELLOW" "📝 Creating Dockerfile.catalog.enhanced..."
cat > Dockerfile.catalog.enhanced << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements_catalog.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements_catalog.txt

# Copy the enhanced catalog manager
COPY catalog_manager_extended.py catalog_manager.py

# Create logs directory
RUN mkdir -p /app/logs

# Create non-root user
RUN useradd -m -u 1000 cataloguser && \
    chown -R cataloguser:cataloguser /app

USER cataloguser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Expose Flask port
EXPOSE 8080

# Run the Flask app with proper logging
CMD ["python", "-u", "catalog_manager.py"]
EOF

# Create new Dockerfile.mcp.enhanced
print_msg "$YELLOW" "📝 Creating Dockerfile.mcp.enhanced..."
cat > Dockerfile.mcp.enhanced << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements_mcp.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements_mcp.txt

# Copy the enhanced MCP server with 13 tools
COPY mcp_fastmcp_server_extended.py mcp_server.py

# Create logs directory
RUN mkdir -p /app/logs

# Create non-root user
RUN useradd -m -u 1000 mcpuser && \
    chown -R mcpuser:mcpuser /app

USER mcpuser

# Expose MCP server port
EXPOSE 8090

# Run the MCP server with proper logging
CMD ["python", "-u", "mcp_server.py"]
EOF

# Update docker-compose.yml to use enhanced version
print_msg "$YELLOW" "📝 Updating docker-compose.yml..."
if [ -f "docker-compose.extended.yml" ]; then
    # Use the extended compose file as the main one
    cp docker-compose.extended.yml docker-compose.yml
    # Update the Dockerfile references
    sed -i.bak 's/dockerfile: Dockerfile.catalog.extended/dockerfile: Dockerfile.catalog.enhanced/g' docker-compose.yml
    sed -i.bak 's/dockerfile: Dockerfile.mcp.extended/dockerfile: Dockerfile.mcp.enhanced/g' docker-compose.yml
    rm -f docker-compose.yml.bak
else
    print_msg "$RED" "❌ docker-compose.extended.yml not found!"
    exit 1
fi

# Make all scripts executable
print_msg "$YELLOW" "🔧 Setting permissions..."
chmod +x *.sh 2>/dev/null || true

# Create necessary directories
mkdir -p logs/catalog logs/mcp data

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    print_msg "$YELLOW" "📝 Creating .env file..."
    cat > .env << EOF
COMPOSE_PROJECT_NAME=telecom_mcp
DB_HOST=postgres
DB_PORT=5432
DB_NAME=telecom_catalog
DB_USER=telecom_user
DB_PASSWORD=telecom_pass
EOF
fi

print_msg "$GREEN" "\n✅ Updates applied successfully!"
print_msg "$GREEN" "================================"

print_msg "$BLUE" "\n📋 Next Steps:"
print_msg "$NC" "1. Stop any running services:"
print_msg "$YELLOW" "   docker-compose down"
print_msg "$NC" "\n2. Build the enhanced version:"
print_msg "$YELLOW" "   docker-compose build --no-cache"
print_msg "$NC" "\n3. Start the enhanced services:"
print_msg "$YELLOW" "   docker-compose up -d"
print_msg "$NC" "\n4. Verify the deployment:"
print_msg "$YELLOW" "   # Wait 15 seconds for services to start"
print_msg "$YELLOW" "   sleep 15"
print_msg "$YELLOW" "   # Check health"
print_msg "$YELLOW" "   curl http://localhost:8080/health"
print_msg "$YELLOW" "   # Count tools (should be 13)"
print_msg "$YELLOW" "   curl -X POST http://localhost:8090/mcp/stream \\"
print_msg "$YELLOW" "     -H 'Content-Type: application/json' \\"
print_msg "$YELLOW" "     -d '{\"jsonrpc\": \"2.0\", \"method\": \"tools/list\", \"params\": {}, \"id\": 1}'"

print_msg "$GREEN" "\n🎉 Your system is ready to build with 13 tools!"
