#!/bin/bash
# Setup script for Telepath AI MCP demo

echo "Setting up Telepath AI MCP Demo..."
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Install Python dependencies for testing
echo "📦 Installing Python test dependencies..."
if command -v pip3 &> /dev/null; then
    pip3 install -r requirements_test.txt
elif command -v pip &> /dev/null; then
    pip install -r requirements_test.txt
else
    echo "⚠️  pip not found. You'll need to install aiohttp manually for testing."
fi

# Make scripts executable
chmod +x quick_test.sh
chmod +x run_inspector.sh

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Build containers: make build"
echo "2. Start services:   make up"
echo "3. Run tests:        make test-mcp"
echo "4. Use Inspector:    make inspector"
