#!/bin/bash

# 🐧 Enhanced Catalog Manager - Ubuntu Setup Script
# Installs complete Enhanced Catalog Manager on Ubuntu/Debian systems

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_header() {
    echo -e "${BLUE}"
    echo "=============================================="
    echo "🐧 ENHANCED CATALOG MANAGER - UBUNTU SETUP"
    echo "   Production-Ready TMF API Platform"
    echo "=============================================="
    echo -e "${NC}"
}

print_step() {
    echo -e "${GREEN}[STEP $1]${NC} $2"
}

print_substep() {
    echo -e "  ${YELLOW}→${NC} $1"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if running on Ubuntu/Debian
check_ubuntu() {
    if [ ! -f /etc/lsb-release ] && [ ! -f /etc/debian_version ]; then
        print_error "This script is designed for Ubuntu/Debian systems"
        print_error "For other Linux distributions, please modify package installation commands"
        exit 1
    fi
    
    if [ -f /etc/lsb-release ]; then
        source /etc/lsb-release
        print_substep "Detected: $DISTRIB_DESCRIPTION"
    else
        print_substep "Detected: Debian-based system"
    fi
}

# Install system dependencies
install_system_dependencies() {
    print_step "1" "Installing System Dependencies"
    
    # Update package lists
    print_substep "Updating package lists..."
    sudo apt update
    
    # Install Python and development tools
    print_substep "Installing Python development environment..."
    sudo apt install -y \
        python3 \
        python3-dev \
        python3-pip \
        python3-venv \
        python3-setuptools \
        build-essential
    
    # Install PostgreSQL development libraries
    print_substep "Installing PostgreSQL development libraries..."
    sudo apt install -y \
        postgresql \
        postgresql-contrib \
        libpq-dev \
        postgresql-client
    
    # Install Docker
    print_substep "Installing Docker..."
    sudo apt install -y \
        docker.io \
        docker-compose \
        git \
        curl \
        jq \
        wget
    
    # Configure Docker
    print_substep "Configuring Docker..."
    sudo usermod -aG docker $USER
    sudo systemctl start docker
    sudo systemctl enable docker
    
    # Install additional utilities
    sudo apt install -y tree htop net-tools
    
    print_success "System dependencies installed"
    print_warning "Please log out and back in for Docker group changes to take effect"
}

# Setup project directory
setup_project() {
    print_step "2" "Setting Up Project"
    
    PROJECT_DIR="$HOME/enhanced-catalog-manager"
    
    # Create project directory
    if [ -d "$PROJECT_DIR" ]; then
        print_warning "Project directory exists. Backing up..."
        mv "$PROJECT_DIR" "$PROJECT_DIR.backup.$(date +%Y%m%d_%H%M%S)"
    fi
    
    mkdir -p "$PROJECT_DIR"
    cd "$PROJECT_DIR"
    
    # Create directory structure
    mkdir -p {src,config,data,logs,scripts,tests,backups,docs}
    
    print_success "Project directory created: $PROJECT_DIR"
}

# Setup Python environment
setup_python_environment() {
    print_step "3" "Setting Up Python Environment"
    
    cd "$PROJECT_DIR"
    
    # Create virtual environment
    print_substep "Creating virtual environment..."
    python3 -m venv venv
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Upgrade pip
    print_substep "Upgrading pip..."
    pip install --upgrade pip setuptools wheel
    
    # Create Ubuntu-optimized requirements
    print_substep "Creating requirements files..."
    
    cat > requirements_catalog.txt << 'EOF'
Flask>=3.0.0
psycopg2-binary>=2.9.0
python-dotenv>=1.0.0
requests>=2.31.0
Werkzeug>=2.3.7
gunicorn>=21.2.0
aiohttp>=3.8.5
EOF

    cat > requirements_mcp.txt << 'EOF'
aiohttp>=3.9.0
aiohttp-sse>=2.1.0
mcp[fastmcp]>=1.0.0
psycopg2-binary>=2.9.0
pydantic>=2.4.2
typing-extensions>=4.8.0
EOF

    cat > requirements_test.txt << 'EOF'
pytest>=7.4.2
pytest-asyncio>=0.21.1
requests>=2.31.0
coverage>=7.3.2
EOF

    # Install Python dependencies
    print_substep "Installing Python dependencies..."
    pip install -r requirements_catalog.txt
    pip install -r requirements_mcp.txt
    pip install -r requirements_test.txt
    
    # Test imports
    print_substep "Testing Python imports..."
    python3 -c "
import psycopg2
import flask
import aiohttp
import mcp
print('✅ All Python dependencies working!')
"
    
    print_success "Python environment configured"
}

# Create Docker configuration
create_docker_config() {
    print_step "4" "Creating Docker Configuration"
    
    cd "$PROJECT_DIR"
    
    # Create docker-compose.yml
    cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  catalog-manager:
    build:
      context: .
      dockerfile: Dockerfile.catalog
    container_name: catalog-manager
    ports:
      - "8080:8080"
    environment:
      - DATABASE_URL=postgresql://catalog_user:catalog_pass@postgres:5432/catalog_db
      - FLASK_ENV=production
    depends_on:
      - postgres
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  postgres:
    image: postgres:15
    container_name: postgres
    environment:
      - POSTGRES_DB=catalog_db
      - POSTGRES_USER=catalog_user
      - POSTGRES_PASSWORD=catalog_pass
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init_db.sql:/docker-entrypoint-initdb.d/init_db.sql
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U catalog_user -d catalog_db"]
      interval: 30s
      timeout: 10s
      retries: 3

volumes:
  postgres_data:
EOF

    print_success "Docker configuration created"
}

# Create application files
create_app_files() {
    print_step "5" "Creating Application Files"
    
    cd "$PROJECT_DIR"
    
    # Create basic catalog manager
    cat > src/catalog_manager.py << 'EOF'
#!/usr/bin/env python3
"""
Enhanced Catalog Manager - Ubuntu Production Version
"""

from flask import Flask, jsonify, request
import psycopg2
import os
from datetime import datetime

app = Flask(__name__)

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://catalog_user:catalog_pass@localhost:5432/catalog_db')

@app.route('/health')
def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        conn = psycopg2.connect(DATABASE_URL)
        conn.close()
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'database': 'connected',
            'platform': 'ubuntu'
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
        'tmf_apis': ['TMF637', 'TMF629', 'TMF622', 'TMF640'],
        'enhanced_tools': 9,
        'total_tools': 13
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)
EOF

    # Create Dockerfile
    cat > Dockerfile.catalog << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements_catalog.txt .
RUN pip install --no-cache-dir -r requirements_catalog.txt

# Copy application code
COPY src/ ./src/
COPY config/ ./config/

# Create logs directory
RUN mkdir -p logs

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Run application
CMD ["python", "src/catalog_manager.py"]
EOF

    # Create database initialization script
    cat > init_db.sql << 'EOF'
-- Enhanced Catalog Manager Database Schema
-- Ubuntu Production Version

CREATE TABLE IF NOT EXISTS customers (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    phone VARCHAR(50),
    address JSONB,
    account_status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS product_offerings (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(100),
    price_monthly DECIMAL(10,2),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS service_specifications (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    service_type VARCHAR(100),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample data
INSERT INTO customers (id, name, email, phone, account_status) VALUES
('CUST-001', 'Acme Corporation', 'admin@acme.com', '+1-555-0123', 'active'),
('CUST-002', 'Tech Innovations Ltd', 'contact@techinnovations.com', '+1-555-0124', 'active')
ON CONFLICT (id) DO NOTHING;

INSERT INTO product_offerings (id, name, description, category, price_monthly, is_active) VALUES
('FIBER-1000-PRO', 'Fiber Internet 1000 Pro', 'High-speed fiber internet 1000 Mbps', 'internet', 89.99, true),
('MOBILE-UNLIMITED', 'Mobile Unlimited Plan', 'Unlimited mobile data and calls', 'mobile', 65.00, true)
ON CONFLICT (id) DO NOTHING;

INSERT INTO service_specifications (id, name, service_type, description) VALUES
('fiber-internet-1000', 'Fiber Internet 1000', 'fiber_internet', '1000 Mbps fiber internet service'),
('mobile-unlimited-data', 'Mobile Unlimited Data', 'mobile', 'Unlimited mobile data service')
ON CONFLICT (id) DO NOTHING;
EOF

    print_success "Application files created"
}

# Setup and test system
setup_and_test() {
    print_step "6" "Building and Testing System"
    
    cd "$PROJECT_DIR"
    
    # Build Docker containers
    print_substep "Building Docker containers..."
    docker-compose build
    
    # Start services
    print_substep "Starting services..."
    docker-compose up -d
    
    # Wait for services to be ready
    print_substep "Waiting for services to start..."
    sleep 10
    
    # Test health endpoint
    print_substep "Testing health endpoint..."
    for i in {1..30}; do
        if curl -s http://localhost:8080/health > /dev/null; then
            print_success "Health check passed"
            break
        fi
        if [ $i -eq 30 ]; then
            print_error "Health check failed after 30 attempts"
            exit 1
        fi
        sleep 2
    done
    
    # Run comprehensive test
    print_substep "Running system validation..."
    curl -s http://localhost:8080/health | jq '.'
    curl -s http://localhost:8080/api/status | jq '.'
    
    print_success "System is running and validated"
}

# Create management scripts
create_scripts() {
    print_step "7" "Creating Management Scripts"
    
    cd "$PROJECT_DIR"
    
    # Create start script
    cat > scripts/start.sh << 'EOF'
#!/bin/bash
echo "🚀 Starting Enhanced Catalog Manager..."
cd "$(dirname "$0")/.."
docker-compose up -d
echo "✅ System started. Access at http://localhost:8080"
EOF

    # Create stop script
    cat > scripts/stop.sh << 'EOF'
#!/bin/bash
echo "🛑 Stopping Enhanced Catalog Manager..."
cd "$(dirname "$0")/.."
docker-compose down
echo "✅ System stopped"
EOF

    # Create status script
    cat > scripts/status.sh << 'EOF'
#!/bin/bash
echo "📊 Enhanced Catalog Manager Status:"
cd "$(dirname "$0")/.."
docker-compose ps
echo ""
echo "🌐 Health Check:"
curl -s http://localhost:8080/health | jq '.' 2>/dev/null || echo "Service not responding"
EOF

    # Make scripts executable
    chmod +x scripts/*.sh
    
    print_success "Management scripts created"
}

# Final summary
print_final_summary() {
    print_step "8" "Ubuntu Setup Complete!"
    
    echo ""
    echo -e "${GREEN}🐧 ENHANCED CATALOG MANAGER - UBUNTU READY!${NC}"
    echo "=================================================="
    echo ""
    echo "📍 Installation Location: $PROJECT_DIR"
    echo "🌐 Access URL: http://localhost:8080"
    echo "💾 Database: PostgreSQL on port 5432"
    echo ""
    echo "🎮 Management Commands:"
    echo "  Start:  $PROJECT_DIR/scripts/start.sh"
    echo "  Stop:   $PROJECT_DIR/scripts/stop.sh" 
    echo "  Status: $PROJECT_DIR/scripts/status.sh"
    echo ""
    echo "🧪 Quick Tests:"
    echo "  Health: curl http://localhost:8080/health"
    echo "  Status: curl http://localhost:8080/api/status"
    echo ""
    echo "📋 Next Steps:"
    echo "  1. ✅ System is running and validated"
    echo "  2. 📋 Copy your enhanced MCP server files"
    echo "  3. 🔄 Configure Claude Desktop (if needed)"
    echo "  4. 🧪 Test all 13 tools functionality"
    echo ""
    echo -e "${GREEN}🏆 SUCCESS: Enhanced Catalog Manager running on Ubuntu!${NC}"
    echo ""
    
    # Show system info
    echo "📊 System Information:"
    echo "  OS: $(lsb_release -d | cut -f2)"
    echo "  Docker: $(docker --version)"
    echo "  Python: $(python3 --version)"
    echo "  PostgreSQL: Container-based"
    echo ""
}

# Main execution
main() {
    print_header
    
    check_ubuntu
    install_system_dependencies
    setup_project
    setup_python_environment
    create_docker_config
    create_app_files
    setup_and_test
    create_scripts
    print_final_summary
    
    echo -e "${BLUE}Ubuntu setup completed successfully!${NC}"
    echo -e "${YELLOW}Remember to copy your enhanced catalog manager files for full functionality.${NC}"
}

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    print_error "Please don't run this script as root"
    print_error "Run as regular user - script will prompt for sudo when needed"
    exit 1
fi

# Run the setup
main "$@"
