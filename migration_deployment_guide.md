# 🚀 Enhanced Catalog Manager - Migration & Deployment Guide

## 📋 **Moving to a New Machine**

### **Quick Migration (Existing Project)**

If you already have the enhanced catalog manager and want to move it to a new machine:

#### **Step 1: Package Current System**
```bash
# On old machine - create deployment package
cd /Users/joe/dev/mcp_cm_v1
tar -czf telepath-catalog-deployment.tar.gz \
  mcp_server_fixed.py \
  catalog_manager_extended_fixed.py \
  docker-compose.extended.yml \
  init_db_extended.sql \
  requirements_*.txt \
  claude_desktop_config.json

# Transfer to new machine
```

#### **Step 2: Deploy on New Machine**
```bash
# On new machine
mkdir -p ~/telepath-ai-catalog
cd ~/telepath-ai-catalog
tar -xzf telepath-catalog-deployment.tar.gz

# Install dependencies
pip install -r requirements_catalog.txt
pip install -r requirements_mcp.txt

# Start Docker services
docker-compose -f docker-compose.extended.yml up -d

# Update Claude Desktop config
cp claude_desktop_config.json ~/.config/claude_desktop/config.json
```

### **Complete Fresh Setup (Recommended)**

For a completely new setup on a fresh machine:

#### **Step 1: Run Automated Setup**
```bash
# Download and run the setup script
curl -O https://your-repo/setup_enhanced_catalog.sh
chmod +x setup_enhanced_catalog.sh
./setup_enhanced_catalog.sh
```

#### **Step 2: Verify Installation**
```bash
# Navigate to project directory
cd ~/telepath-ai-catalog

# Validate deployment
./scripts/validate_deployment.sh

# Run comprehensive tests
python tests/test_complete_system.py
```

## 🏗️ **Production Deployment**

### **Environment Setup**

#### **Production Environment Variables**
```bash
# Create production environment file
cat > .env.production << 'EOF'
# Database Configuration
DB_HOST=your-postgres-host
DB_PORT=5432
DB_NAME=telecom_catalog_prod
DB_USER=telecom_prod_user
DB_PASSWORD=your-secure-password

# API Configuration
API_HOST=0.0.0.0
API_PORT=8080
DEBUG=false
LOG_LEVEL=INFO

# Security
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=your-domain.com,localhost

# Performance
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=10
REDIS_URL=redis://your-redis-host:6379
EOF
```

#### **Production Docker Compose**
```yaml
# docker-compose.production.yml
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: ${DB_NAME}
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    networks:
      - telecom_network
    restart: unless-stopped

  catalog-manager:
    build:
      context: .
      dockerfile: Dockerfile.production
    environment:
      - DB_HOST=postgres
      - DB_NAME=${DB_NAME}
      - DB_USER=${DB_USER}
      - DB_PASSWORD=${DB_PASSWORD}
      - DEBUG=false
      - LOG_LEVEL=INFO
    ports:
      - "8080:8080"
    depends_on:
      - postgres
    networks:
      - telecom_network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/ssl/certs
    depends_on:
      - catalog-manager
    networks:
      - telecom_network
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    networks:
      - telecom_network
    restart: unless-stopped

volumes:
  postgres_data:

networks:
  telecom_network:
    driver: bridge
```

### **Production Dockerfile**
```dockerfile
# Dockerfile.production
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Copy requirements and install Python dependencies
COPY --chown=app:app requirements_catalog.txt .
RUN pip install --user --no-cache-dir -r requirements_catalog.txt

# Copy application code
COPY --chown=app:app src/ .

# Create logs directory
RUN mkdir -p logs

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Run application with gunicorn
CMD ["python", "-m", "gunicorn", "--bind", "0.0.0.0:8080", "--workers", "4", "--worker-class", "sync", "--timeout", "120", "catalog_manager:app"]
```

## 🔄 **Continuous Deployment**

### **CI/CD Pipeline (GitHub Actions)**
```yaml
# .github/workflows/deploy.yml
name: Deploy Enhanced Catalog Manager

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements_test.txt
          pip install -r requirements_catalog.txt
      
      - name: Run tests
        run: |
          docker-compose up -d postgres
          sleep 30
          python tests/test_complete_system.py
      
      - name: Cleanup
        run: docker-compose down

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to production
        env:
          DEPLOY_HOST: ${{ secrets.DEPLOY_HOST }}
          DEPLOY_USER: ${{ secrets.DEPLOY_USER }}
          DEPLOY_KEY: ${{ secrets.DEPLOY_KEY }}
        run: |
          echo "$DEPLOY_KEY" | base64 -d > deploy_key
          chmod 600 deploy_key
          
          scp -i deploy_key -o StrictHostKeyChecking=no \
            docker-compose.production.yml \
            $DEPLOY_USER@$DEPLOY_HOST:/opt/telepath-catalog/
          
          ssh -i deploy_key -o StrictHostKeyChecking=no \
            $DEPLOY_USER@$DEPLOY_HOST \
            "cd /opt/telepath-catalog && docker-compose -f docker-compose.production.yml up -d --build"
```

## 🔒 **Security Configuration**

### **SSL/TLS Configuration**
```nginx
# nginx.conf
events {
    worker_connections 1024;
}

http {
    upstream catalog_backend {
        server catalog-manager:8080;
    }

    server {
        listen 80;
        server_name your-domain.com;
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name your-domain.com;

        ssl_certificate /etc/ssl/certs/cert.pem;
        ssl_certificate_key /etc/ssl/certs/key.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384;

        location / {
            proxy_pass http://catalog_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        location /health {
            proxy_pass http://catalog_backend/health;
            access_log off;
        }
    }
}
```

### **Database Security**
```sql
-- Create read-only user for monitoring
CREATE USER monitoring_user WITH PASSWORD 'monitoring_password';
GRANT CONNECT ON DATABASE telecom_catalog TO monitoring_user;
GRANT USAGE ON SCHEMA public TO monitoring_user;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO monitoring_user;

-- Create backup user
CREATE USER backup_user WITH PASSWORD 'backup_password';
GRANT CONNECT ON DATABASE telecom_catalog TO backup_user;
GRANT USAGE ON SCHEMA public TO backup_user;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO backup_user;

-- Set up row-level security (example)
ALTER TABLE customers ENABLE ROW LEVEL SECURITY;
CREATE POLICY customer_isolation ON customers
    FOR ALL TO app_user
    USING (tenant_id = current_setting('app.tenant_id'));
```

## 📊 **Monitoring & Observability**

### **Health Monitoring**
```bash
#!/bin/bash
# scripts/monitor_health.sh

while true; do
    if ! curl -sf http://localhost:8080/health > /dev/null; then
        echo "$(date): Health check failed!" | tee -a /var/log/catalog-health.log
        # Send alert (email, Slack, etc.)
    fi
    sleep 60
done
```

### **Log Aggregation**
```yaml
# docker-compose.logging.yml
version: '3.8'

services:
  filebeat:
    image: docker.elastic.co/beats/filebeat:8.5.0
    volumes:
      - ./logs:/var/log/app:ro
      - ./filebeat.yml:/usr/share/filebeat/filebeat.yml
    depends_on:
      - elasticsearch

  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.5.0
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
    ports:
      - "9200:9200"

  kibana:
    image: docker.elastic.co/kibana/kibana:8.5.0
    ports:
      - "5601:5601"
    depends_on:
      - elasticsearch
```

## 🔧 **Configuration Management**

### **Environment-Specific Configs**
```python
# config/environments.py
import os

class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_PORT = int(os.environ.get('DB_PORT', 5432))
    DB_NAME = os.environ.get('DB_NAME', 'telecom_catalog')
    DB_USER = os.environ.get('DB_USER', 'telecom_user')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', 'telecom_pass')

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    LOG_LEVEL = 'INFO'
    SSL_REQUIRED = True

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DB_NAME = 'telecom_catalog_test'

# Configuration selection
config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig
}
```

## 📈 **Performance Optimization**

### **Database Optimization**
```sql
-- Performance indexes
CREATE INDEX CONCURRENTLY idx_orders_customer_date ON orders(customer_id, order_date);
CREATE INDEX CONCURRENTLY idx_service_coverage_location_type ON service_coverage(location_id, service_type);
CREATE INDEX CONCURRENTLY idx_customers_status_city ON customers(account_status, city);

-- Materialized views for common queries
CREATE MATERIALIZED VIEW customer_order_summary AS
SELECT 
    c.id,
    c.name,
    COUNT(o.id) as total_orders,
    SUM(o.total_amount) as total_spent,
    MAX(o.order_date) as last_order_date
FROM customers c
LEFT JOIN orders o ON c.id = o.customer_id
GROUP BY c.id, c.name;

-- Refresh strategy
CREATE OR REPLACE FUNCTION refresh_materialized_views()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY customer_order_summary;
END;
$$ LANGUAGE plpgsql;

-- Schedule refresh (with pg_cron extension)
SELECT cron.schedule('refresh-views', '0 2 * * *', 'SELECT refresh_materialized_views();');
```

### **API Performance**
```python
# Performance middleware
from flask import request, jsonify
import time
import logging

def add_performance_monitoring(app):
    @app.before_request
    def before_request():
        request.start_time = time.time()
    
    @app.after_request
    def after_request(response):
        duration = time.time() - request.start_time
        if duration > 1.0:  # Log slow requests
            logging.warning(f"Slow request: {request.method} {request.path} took {duration:.2f}s")
        
        response.headers['X-Response-Time'] = f"{duration:.3f}s"
        return response
```

## 🚨 **Disaster Recovery**

### **Backup Strategy**
```bash
#!/bin/bash
# scripts/backup.sh

BACKUP_DIR="/backups/$(date +%Y%m%d)"
mkdir -p "$BACKUP_DIR"

# Database backup
docker-compose exec -T postgres pg_dump -U telecom_user telecom_catalog | \
    gzip > "$BACKUP_DIR/database_$(date +%H%M%S).sql.gz"

# Application backup
tar -czf "$BACKUP_DIR/application_$(date +%H%M%S).tar.gz" \
    src/ config/ docker-compose.*.yml

# Upload to cloud storage (example: AWS S3)
aws s3 sync "$BACKUP_DIR" "s3://your-backup-bucket/$(date +%Y%m%d)/"

# Clean old local backups (keep 7 days)
find /backups -type d -mtime +7 -exec rm -rf {} \;
```

### **Recovery Procedures**
```bash
#!/bin/bash
# scripts/restore.sh

BACKUP_DATE=$1
if [ -z "$BACKUP_DATE" ]; then
    echo "Usage: $0 YYYYMMDD"
    exit 1
fi

# Download from cloud storage
aws s3 sync "s3://your-backup-bucket/$BACKUP_DATE" "/tmp/restore/"

# Stop services
docker-compose down

# Restore database
gunzip -c "/tmp/restore/database_*.sql.gz" | \
    docker-compose exec -T postgres psql -U telecom_user telecom_catalog

# Restore application
tar -xzf "/tmp/restore/application_*.tar.gz" -C .

# Restart services
docker-compose up -d

echo "Recovery complete for $BACKUP_DATE"
```

---

## 📞 **Support & Maintenance**

### **Regular Maintenance Tasks**
- **Daily**: Monitor health checks and error logs
- **Weekly**: Review performance metrics and slow queries
- **Monthly**: Update dependencies and security patches
- **Quarterly**: Full backup and disaster recovery testing

### **Emergency Contacts**
- **System Administrator**: [contact info]
- **Database Administrator**: [contact info]
- **Development Team**: [contact info]

---

**🎯 This guide provides complete instructions for deploying and maintaining the Enhanced Catalog Manager in any environment, from development to enterprise production.**