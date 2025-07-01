.PHONY: build up down logs clean test-mcp

# Build all containers
build:
	docker-compose build

# Start all services
up:
	docker-compose up -d
	@echo "Waiting for services to be ready..."
	@sleep 10
	@echo "Services are ready!"
	@echo "Catalog Manager API: http://localhost:8080"
	@echo "MCP Server: Available on stdio"

# Stop all services
down:
	docker-compose down

# View logs
logs:
	docker-compose logs -f

# Clean up everything
clean:
	docker-compose down -v
	docker system prune -f

# Test the MCP server with inspector
test-mcp:
	@echo "To test the MCP server with Anthropic's inspector:"
	@echo "1. Install MCP inspector: npm install -g @anthropic/mcp-inspector"
	@echo "2. Run: docker exec -it mcp_server python mcp_server.py"
	@echo "3. In another terminal: mcp-inspector"
	@echo ""
	@echo "Or use the provided test script:"
	python test_mcp.py

# Individual service commands
postgres:
	docker-compose up -d postgres

catalog:
	docker-compose up -d catalog-manager

mcp:
	docker-compose up -d mcp-server

# Health checks
health:
	@echo "Checking service health..."
	@curl -s http://localhost:8080/health | jq . || echo "Catalog Manager not healthy"
	@docker-compose ps

# Database shell
db-shell:
	docker exec -it telecom_postgres psql -U telecom_user -d telecom_catalog
