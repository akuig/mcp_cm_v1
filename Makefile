.PHONY: build up down logs clean test-mcp test-curl inspector

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
	@echo "MCP Server: http://localhost:8090"
	@echo "MCP Streaming endpoint: http://localhost:8090/mcp/stream"

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

# Test the MCP server
test-mcp:
	@echo "Testing MCP server with HTTP streaming transport:"
	@echo "MCP Server endpoint: http://localhost:8090/mcp/stream"
	@echo "Installing test dependencies..."
	@pip3 install -q -r requirements_test.txt 2>/dev/null || pip install -q -r requirements_test.txt
	@echo "Running automated tests..."
	python3 test_mcp.py

# Setup Python virtual environment for testing
venv:
	@echo "Setting up Python virtual environment..."
	python3 -m venv venv
	@echo "Activate with: source venv/bin/activate"
	@echo "Then run: pip install -r requirements_test.txt"

# Test with curl
test-curl:
	@echo "Testing MCP server with curl:"
	@echo "Listing tools:"
	@curl -X POST http://localhost:8090/mcp/stream \
		-H "Content-Type: application/json" \
		-H "Accept: application/json-stream" \
		-d '{"jsonrpc": "2.0", "method": "tools/list", "params": {}, "id": 1}' | jq .
	@echo "\n\nInitializing MCP:"
	@curl -X POST http://localhost:8090/mcp/stream \
		-H "Content-Type: application/json" \
		-H "Accept: application/json-stream" \
		-d '{"jsonrpc": "2.0", "method": "initialize", "params": {}, "id": 2}' | jq .

# Run MCP Inspector with bridge
inspector:
	@echo "Starting MCP Inspector with HTTP streaming bridge..."
	@echo "Make sure services are running (make up)"
	@echo ""
	@if ! command -v mcp-inspector > /dev/null; then \
		echo "Installing MCP Inspector..."; \
		npm install -g @anthropic/mcp-inspector; \
	fi
	@echo "Starting bridge in background..."
	@python mcp_bridge.py &
	@BRIDGE_PID=$$!; \
	sleep 2; \
	echo "Starting MCP Inspector..."; \
	mcp-inspector stdio; \
	kill $$BRIDGE_PID 2>/dev/null || true

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
	@echo "Catalog Manager:"
	@curl -s http://localhost:8080/health | jq . || echo "Catalog Manager not healthy"
	@echo "\nMCP Server:"
	@curl -s http://localhost:8090/health | jq . || echo "MCP Server not healthy"
	@echo "\nContainer status:"
	@docker-compose ps

# Database shell
db-shell:
	docker exec -it telecom_postgres psql -U telecom_user -d telecom_catalog

# Reset database
reset-db:
	@chmod +x reset_db.sh
	./reset_db.sh
