#!/bin/bash
# Quick fix for Claude Desktop MCP connection

echo "🤖 Fixing Claude Desktop MCP Connection"
echo "======================================"
echo ""
echo "You're seeing ngrok errors because Claude Desktop needs STDIO protocol,"
echo "not HTTP endpoints. Let's fix this!"
echo ""

# Step 1: Check Python
echo "1️⃣ Checking Python and dependencies..."
if command -v python3 &> /dev/null; then
    echo "   ✅ Python3 found"
else
    echo "   ❌ Python3 not found. Please install Python 3"
    exit 1
fi

# Install MCP if needed
pip3 show mcp > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "   📦 Installing MCP SDK..."
    pip3 install mcp aiohttp
else
    echo "   ✅ MCP SDK already installed"
fi

# Step 2: Check services
echo ""
echo "2️⃣ Checking local services..."
if curl -s http://localhost:8080/health > /dev/null 2>&1; then
    echo "   ✅ Catalog Manager is running"
else
    echo "   ❌ Catalog Manager not running. Starting services..."
    docker-compose -f docker-compose-with-fault.yml up -d
    sleep 10
fi

if curl -s http://localhost:8081/health > /dev/null 2>&1; then
    echo "   ✅ Fault Manager is running"
else
    echo "   ❌ Fault Manager not running. Starting services..."
    docker-compose -f docker-compose-with-fault.yml up -d fault-manager
    sleep 10
fi

# Step 3: Test MCP
echo ""
echo "3️⃣ Testing MCP server..."
python3 test_mcp_stdio.py
if [ $? -ne 0 ]; then
    echo "   ❌ MCP test failed. Check the errors above."
    exit 1
fi

# Step 4: Configure Claude Desktop
echo ""
echo "4️⃣ Configuring Claude Desktop..."
CLAUDE_CONFIG_DIR="$HOME/Library/Application Support/Claude"
CLAUDE_CONFIG_FILE="$CLAUDE_CONFIG_DIR/claude_desktop_config.json"

# Create directory if it doesn't exist
mkdir -p "$CLAUDE_CONFIG_DIR"

# Backup existing config if it exists
if [ -f "$CLAUDE_CONFIG_FILE" ]; then
    echo "   📋 Backing up existing config to claude_desktop_config.backup.json"
    cp "$CLAUDE_CONFIG_FILE" "$CLAUDE_CONFIG_DIR/claude_desktop_config.backup.json"
fi

# Copy new config
echo "   📝 Installing new configuration..."
cp claude_desktop_config_local.json "$CLAUDE_CONFIG_FILE"

echo ""
echo "✅ Setup Complete!"
echo ""
echo "📝 Next Steps:"
echo "1. Quit Claude Desktop completely (Cmd+Q)"
echo "2. Start Claude Desktop again"
echo "3. Click the 🔌 icon and look for 'telepath-fault-local'"
echo "4. Try asking: 'Check for service issues at 123 Main Street Dublin'"
echo ""
echo "🚨 Important: Do NOT use ngrok - services must run on localhost!"
echo ""
echo "If you still have issues, check the logs at:"
echo "~/Library/Logs/Claude/"
