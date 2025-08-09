#!/bin/bash
# Make all scripts executable

echo "Making scripts executable..."
chmod +x *.sh 2>/dev/null || true
echo "✅ All scripts are now executable"
echo ""
echo "Available commands:"
echo "• make restart-with-orders  - Restart with order management tool"
echo "• ./restart_with_order_tool.sh - Direct script execution"
echo ""
