# 🚀 Enhanced Catalog Manager - Complete Setup Guide

## 📋 **Overview**

This guide provides complete instructions for setting up the Telepath AI Enhanced Catalog Manager on a new machine. The system implements TMF (TeleManagement Forum) standards for telecom operations with enhanced catalog management capabilities.

## 🏗️ **System Architecture**

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Claude AI     │◄──►│  MCP Server      │◄──►│ Catalog Manager │
│   (Desktop)     │    │  (13 Tools)      │    │ (Flask API)     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │                         │
                                │                         ▼
                                │               ┌─────────────────┐
                                │               │  PostgreSQL     │
                                │               │  Database       │
                                │               └─────────────────┘
                                │
                                ▼
                    ┌──────────────────────┐
                    │  Docker Environment  │
                    │  (Containers)        │
                    └──────────────────────┘
```

## 🎯 **Components**

### **Core TMF APIs** (4 tools)
- **TMF637**: Service Qualification
- **TMF629**: Customer Management 
- **TMF622**: Product Ordering (Create/List)
- **TMF640**: Service Activation

### **Enhanced Catalog APIs** (9 tools)
- **order_management**: List/retrieve orders with filtering
- **list_service_specifications**: Browse service catalog
- **list_product_offerings**: Browse product catalog
- **list_geographic_locations**: Coverage management
- **sync_catalog_data**: Data integrity tools
- **create_service_specification**: Add new services
- **create_product_offering**: Add new products
- **link_offering_to_specification**: Connect products to services
- **add_geographic_coverage**: Expand service areas

## 📋 **Prerequisites**

### **System Requirements**
- **Operating System**: macOS, Linux, or Windows with WSL2
- **RAM**: Minimum 8GB, Recommended 16GB
- **Storage**: 5GB free space
- **Network**: Internet connection for dependencies

### **Required Software**
- **Python 3.8+** with pip
- **Docker Desktop** (latest version)
- **Git** (for version control)
- **curl** (for API testing)
- **Claude Desktop** (installed and configured)

## 🛠️ **Step-by-Step Setup**

### **Phase 1: Environment Preparation**

#### **1.1 Install System Dependencies**

**macOS:**
```bash
# Install Homebrew if not present
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install dependencies
brew install python@3.11 docker git curl
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install -y python3 python3-pip docker.io docker-compose git curl
sudo usermod -aG docker $USER
```

**Windows (WSL2):**
```bash
# Install Python and Docker Desktop for Windows
# Then in WSL2:
sudo apt update
sudo apt install -y python3 python3-pip git curl
```

#### **1.2 Verify Installations**
```bash
python3 --version  # Should be 3.8+
docker --version   # Should be latest
git --version      # Any recent version
curl --version     # Any recent version
```

### **Phase 2: Project Setup**

#### **2.1 Create Project Structure**
```bash
# Create project directory
mkdir -p ~/telepath-ai-catalog
cd ~/telepath-ai-catalog

# Create subdirectories
mkdir -p {src,config,data,logs,scripts,tests}
```

#### **2.2 Initialize Python Environment**
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Upgrade pip
pip install --upgrade pip
```

#### **2.3 Install Python Dependencies**
```bash
# Create requirements files
cat > requirements_catalog.txt << 'EOF'
Flask==2.3.3
psycopg2-binary==2.9.7
python-dotenv==1.0.0
requests==2.31.0
uuid==1.30
Werkzeug==2.3.7
EOF

cat > requirements_mcp.txt << 'EOF'
mcp==1.0.0
aiohttp==3.8.5
asyncio-mqtt==0.11.1
pydantic==2.4.2
typing-extensions==4.8.0
EOF

# Install dependencies
pip install -r requirements_catalog.txt
pip install -r requirements_mcp.txt
```

### **Phase 3: Database Setup**

#### **3.1 Create Docker Compose Configuration**
```yaml
# docker-compose.yml
version: '3.8'

services:
  postgres:
    image: postgres:15
    container_name: telecom_postgres
    environment:
      POSTGRES_DB: telecom_catalog
      POSTGRES_USER: telecom_user
      POSTGRES_PASSWORD: telecom_pass
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init_db.sql:/docker-entrypoint-initdb.d/init_db.sql
    networks:
      - telecom_network

  catalog-manager:
    build:
      context: .
      dockerfile: Dockerfile.catalog
    container_name: catalog_manager
    ports:
      - "8080:8080"
    environment:
      DB_HOST: postgres
      DB_PORT: 5432
      DB_NAME: telecom_catalog
      DB_USER: telecom_user
      DB_PASSWORD: telecom_pass
    depends_on:
      - postgres
    networks:
      - telecom_network
    volumes:
      - ./logs:/app/logs

volumes:
  postgres_data:

networks:
  telecom_network:
    driver: bridge
```

#### **3.2 Create Database Schema**
```sql
-- init_db.sql
-- TMF-compliant database schema for enhanced catalog manager

-- Customers table (TMF629)
CREATE TABLE customers (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    account_status VARCHAR(50) DEFAULT 'active',
    credit_score INTEGER DEFAULT 0,
    has_overdue_payments BOOLEAN DEFAULT false,
    street_number VARCHAR(20),
    street_name VARCHAR(255),
    city VARCHAR(100),
    postal_code VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Service specifications table
CREATE TABLE service_specifications (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    service_type VARCHAR(100) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Product offerings table
CREATE TABLE product_offerings (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(100),
    price_monthly DECIMAL(10,2),
    price_setup DECIMAL(10,2) DEFAULT 0.00,
    contract_length_months INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Product offering to service specification links
CREATE TABLE offering_service_links (
    id SERIAL PRIMARY KEY,
    product_offering_id VARCHAR(50) REFERENCES product_offerings(id),
    service_specification_id VARCHAR(50) REFERENCES service_specifications(id),
    is_primary BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Geographic locations
CREATE TABLE geographic_locations (
    id VARCHAR(50) PRIMARY KEY,
    city VARCHAR(100) NOT NULL,
    state_province VARCHAR(100),
    country VARCHAR(100) DEFAULT 'US',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Service coverage
CREATE TABLE service_coverage (
    id SERIAL PRIMARY KEY,
    location_id VARCHAR(50) REFERENCES geographic_locations(id),
    service_type VARCHAR(100) NOT NULL,
    available BOOLEAN DEFAULT true,
    max_speed_mbps INTEGER,
    coverage_quality VARCHAR(50) DEFAULT 'good',
    technology VARCHAR(100),
    signal_strength INTEGER,
    street_name VARCHAR(255),
    city VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Orders table (TMF622)
CREATE TABLE orders (
    id VARCHAR(50) PRIMARY KEY,
    order_date DATE,
    external_id VARCHAR(100),
    customer_id VARCHAR(50) REFERENCES customers(id),
    product_offering_id VARCHAR(50) REFERENCES product_offerings(id),
    status VARCHAR(50) DEFAULT 'created',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Order addresses
CREATE TABLE order_addresses (
    id SERIAL PRIMARY KEY,
    order_id VARCHAR(50) REFERENCES orders(id),
    street_number VARCHAR(20),
    street_name VARCHAR(255),
    city VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Service activations (TMF640)
CREATE TABLE service_activations (
    id VARCHAR(50) PRIMARY KEY,
    service_name VARCHAR(255),
    service_type VARCHAR(100),
    service_specification_id VARCHAR(50) REFERENCES service_specifications(id),
    status VARCHAR(50) DEFAULT 'activated',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Activation addresses
CREATE TABLE activation_addresses (
    id SERIAL PRIMARY KEY,
    activation_id VARCHAR(50) REFERENCES service_activations(id),
    street_number VARCHAR(20),
    street_name VARCHAR(255),
    city VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample data
INSERT INTO customers (id, name, account_status, credit_score, has_overdue_payments, street_number, street_name, city, postal_code) VALUES
('8452934', 'Jane Doe', 'active', 720, false, '456', 'Main Street', 'Springfield', '01101'),
('8452935', 'John Smith', 'active', 680, false, '123', 'Oak Avenue', 'Springfield', '01102'),
('8452936', 'Alice Johnson', 'active', 750, false, '789', 'Pine Road', 'Springfield', '01103'),
('8452937', 'Bob Williams', 'suspended', 620, true, '321', 'Elm Street', 'Springfield', '01104'),
('8452938', 'Carol Brown', 'active', 800, false, '654', 'Maple Drive', 'Springfield', '01105'),
('8452939', 'David Lee', 'active', 710, false, '987', 'Cedar Lane', 'Springfield', '01106');

INSERT INTO service_specifications (id, name, service_type, description) VALUES
('fiber-internet-basic', 'Fiber Internet Basic', 'fiber_internet', '100 Mbps fiber internet service'),
('fiber-internet-premium', 'Fiber Internet Premium', 'fiber_internet', '1 Gbps fiber internet service'),
('cable-internet-standard', 'Cable Internet Standard', 'cable_internet', '200 Mbps cable internet service'),
('mobile-5g-unlimited', 'Mobile 5G Unlimited', 'mobile', 'Unlimited 5G mobile service'),
('tv-premium-package', 'TV Premium Package', 'tv', 'Premium TV package with 500+ channels'),
('voice-basic-plan', 'Voice Basic Plan', 'voice', 'Basic voice service with unlimited local calls'),
('wireless-broadband', 'Wireless Broadband', 'wireless_broadband', 'Fixed wireless broadband service');

INSERT INTO product_offerings (id, name, description, category, price_monthly, price_setup, contract_length_months, is_active) VALUES
('fiber-1gb', 'Fiber 1GB Internet', 'High-speed 1 Gbps fiber internet', 'internet', 79.99, 99.99, 12, true),
('cable-200mb', 'Cable 200MB Internet', 'Reliable 200 Mbps cable internet', 'internet', 59.99, 49.99, 12, true),
('mobile-unlimited', 'Mobile Unlimited Plan', 'Unlimited 5G mobile with hotspot', 'mobile', 85.00, 0.00, 24, true),
('tv-premium', 'Premium TV Package', '500+ channels with premium content', 'tv', 129.99, 0.00, 24, true),
('bundle-triple-play', 'Triple Play Bundle', 'Internet + TV + Voice bundle', 'bundle', 149.99, 99.99, 24, true),
('business-fiber', 'Business Fiber', 'Enterprise-grade fiber service', 'business', 299.99, 199.99, 36, true);

INSERT INTO geographic_locations (id, city, state_province, country) VALUES
('springfield-ma', 'Springfield', 'Massachusetts', 'US'),
('boston-ma', 'Boston', 'Massachusetts', 'US'),
('worcester-ma', 'Worcester', 'Massachusetts', 'US'),
('cambridge-ma', 'Cambridge', 'Massachusetts', 'US'),
('lowell-ma', 'Lowell', 'Massachusetts', 'US');

INSERT INTO service_coverage (location_id, service_type, available, max_speed_mbps, coverage_quality, technology, street_name, city) VALUES
('springfield-ma', 'fiber_internet', true, 1000, 'excellent', 'fiber', 'Main Street', 'Springfield'),
('springfield-ma', 'cable_internet', true, 200, 'good', 'cable', 'Main Street', 'Springfield'),
('springfield-ma', 'mobile', true, null, 'excellent', '5G', 'Main Street', 'Springfield'),
('boston-ma', 'fiber_internet', true, 1000, 'excellent', 'fiber', 'Beacon Street', 'Boston'),
('worcester-ma', 'cable_internet', true, 100, 'fair', 'cable', 'Highland Street', 'Worcester');

-- Link offerings to specifications
INSERT INTO offering_service_links (product_offering_id, service_specification_id, is_primary) VALUES
('fiber-1gb', 'fiber-internet-premium', true),
('cable-200mb', 'cable-internet-standard', true),
('mobile-unlimited', 'mobile-5g-unlimited', true),
('tv-premium', 'tv-premium-package', true),
('bundle-triple-play', 'fiber-internet-premium', true),
('bundle-triple-play', 'tv-premium-package', false),
('bundle-triple-play', 'voice-basic-plan', false);

-- Sample orders
INSERT INTO orders (id, order_date, external_id, customer_id, product_offering_id, status) VALUES
('ORD-2025-001', '2025-07-30', 'EXT-001', '8452934', 'fiber-1gb', 'created'),
('ORD-2025-002', '2025-07-29', 'EXT-002', '8452935', 'cable-200mb', 'processing'),
('ORD-2025-003', '2025-07-28', 'EXT-003', '8452936', 'mobile-unlimited', 'completed');

INSERT INTO order_addresses (order_id, street_number, street_name, city) VALUES
('ORD-2025-001', '456', 'Main Street', 'Springfield'),
('ORD-2025-002', '123', 'Oak Avenue', 'Springfield'),
('ORD-2025-003', '789', 'Pine Road', 'Springfield');
```

### **Phase 4: Application Development**

#### **4.1 Create Dockerfile for Catalog Manager**
```dockerfile
# Dockerfile.catalog
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements_catalog.txt .
RUN pip install --no-cache-dir -r requirements_catalog.txt

# Copy application code
COPY src/catalog_manager.py .
COPY src/config.py .

# Create logs directory
RUN mkdir -p logs

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Run application
CMD ["python", "catalog_manager.py"]
```

### **Phase 5: Testing & Validation**

#### **5.1 Create Test Suite**
```python
# tests/test_catalog_manager.py
import unittest
import requests
import json
from typing import Dict, Any

class TestCatalogManager(unittest.TestCase):
    """Test suite for catalog manager"""
    
    BASE_URL = "http://localhost:8080"
    
    def setUp(self):
        """Set up test environment"""
        self.session = requests.Session()
    
    def test_health_check(self):
        """Test health endpoint"""
        response = self.session.get(f"{self.BASE_URL}/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'healthy')
    
    def test_tmf629_customer_management(self):
        """Test TMF629 customer management"""
        customer_id = "8452934"
        response = self.session.get(f"{self.BASE_URL}/tmf629/customer/{customer_id}")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(data['id'], customer_id)
        self.assertIn('name', data)
        self.assertIn('accountStatus', data)
    
    def test_tmf622_order_management_list(self):
        """Test TMF622 order management returns list"""
        response = self.session.get(f"{self.BASE_URL}/tmf622/productOrder?limit=5")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIsInstance(data, list, "TMF622 should return list format")
    
    def test_enhanced_service_specifications(self):
        """Test enhanced service specifications API"""
        response = self.session.get(f"{self.BASE_URL}/api/service-specifications?limit=3")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertIsInstance(data, list)
        if data:
            self.assertIn('id', data[0])
            self.assertIn('name', data[0])
            self.assertIn('service_type', data[0])

if __name__ == '__main__':
    unittest.main()
```

## 🔧 **Troubleshooting Guide**

### **Common Issues & Solutions**

#### **Docker Issues**
```bash
# If containers won't start
docker-compose down
docker system prune -f
docker-compose up --build

# Check logs
docker-compose logs catalog-manager
docker-compose logs postgres
```

#### **Database Connection Issues**
```bash
# Test database connection
docker exec -it telecom_postgres psql -U telecom_user -d telecom_catalog -c "SELECT COUNT(*) FROM customers;"

# Reset database
docker-compose down -v
docker-compose up -d
```

#### **MCP Server Issues**
```bash
# Check Python dependencies
pip list | grep mcp
pip list | grep aiohttp

# Test MCP server manually
python3 mcp_server_fixed.py
```

## 📚 **Additional Resources**

### **Documentation Links**
- [TMF APIs Documentation](https://www.tmforum.org/resources/interface/tmf629-customer-management-api-rest-specification-r19-0-1/)
- [MCP Protocol Documentation](https://modelcontextprotocol.io/docs)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

### **Architecture Decisions**
- **Flask**: Lightweight, well-documented web framework
- **PostgreSQL**: ACID-compliant database with excellent JSON support
- **Docker**: Containerization for consistent deployment
- **MCP**: Direct integration with Claude Desktop
- **TMF Standards**: Industry-standard telecom APIs

## 🎯 **Performance Optimization**

### **Database Optimization**
```sql
-- Add indexes for common queries
CREATE INDEX idx_customers_account_status ON customers(account_status);
CREATE INDEX idx_orders_customer_id ON orders(customer_id);
CREATE INDEX idx_orders_created_at ON orders(created_at);
CREATE INDEX idx_service_coverage_location_service ON service_coverage(location_id, service_type);
```

### **API Optimization**
- Implement connection pooling
- Add response caching for static data
- Use pagination for large datasets
- Add rate limiting for production

## 🔒 **Security Considerations**

### **Production Security**
- Use environment variables for all secrets
- Implement API authentication
- Add input validation and sanitization
- Use HTTPS in production
- Regular security updates

### **Network Security**
```yaml
# production-docker-compose.yml
networks:
  telecom_network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
```

---

**📝 This guide provides a complete foundation for deploying the Enhanced Catalog Manager on any new machine with full TMF compliance and advanced catalog management capabilities.**