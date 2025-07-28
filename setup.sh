#!/bin/bash
# Quick setup script - makes all scripts executable and provides setup guidance

echo "🚀 Enhanced Telecom MCP Quick Setup"
echo "==================================="

# Make all scripts executable
echo "Making scripts executable..."
chmod +x *.sh 2>/dev/null || true
echo "✅ All scripts are now executable"

echo ""
echo "📋 Setup Options:"
echo ""
echo "1. 🔧 Fix Current Database Issues:"
echo "   ./fix_database_setup.sh"
echo "   or: make fix-database"
echo ""
echo "2. 🔄 Fresh Enhanced Database Reset:"
echo "   ./reset_db_enhanced.sh"
echo "   or: make reset-db"
echo ""
echo "3. ✅ Verify Database State:"
echo "   ./verify_db_enhanced.sh"
echo "   or: make verify-db"
echo ""
echo "4. 🚀 Full Enhanced Deployment:"
echo "   make enhanced-deploy"
echo ""
echo "5. 🧪 Test Everything:"
echo "   make enhanced-test"
echo ""

echo "💡 Recommended Steps:"
echo "1. Run: ./fix_database_setup.sh"
echo "2. Test: make enhanced-test"
echo "3. Use: Your MCP tools should now work!"
echo ""

echo "📚 Available Make Commands:"
echo "  make help                - Show all available commands"
echo "  make enhanced-up         - Start enhanced services"
echo "  make enhanced-logs       - View service logs"
echo "  make inspector           - Open MCP Inspector"
echo "  make show-endpoints      - Show all API endpoints"
echo ""
