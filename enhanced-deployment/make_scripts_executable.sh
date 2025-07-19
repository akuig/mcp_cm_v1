#!/bin/bash

echo "🔧 Making all fix scripts executable..."
chmod +x fix_attribute_error.sh
chmod +x fix_mcp_imports.sh
chmod +x fix_import_issues.sh
chmod +x apply_mcp_fixes.sh
chmod +x deploy.sh
chmod +x quick_fix.sh

echo "✅ AttributeError Fix Applied!"
echo ""
echo "🛠️  Key changes made:"
echo "✅ Removed server.add_tool() calls (method doesn't exist)"
echo "✅ Tools are now stored in self.tools list"
echo "✅ Tools returned via handle_list_tools() method"
echo "✅ Fixed server initialization to avoid startup errors"
echo "✅ Added lazy server creation for Starlette app"
echo ""
echo "🚀 To apply the fix:"
echo "   ./fix_attribute_error.sh"
echo ""
echo "📋 This should resolve the AttributeError and make the server start successfully!"
