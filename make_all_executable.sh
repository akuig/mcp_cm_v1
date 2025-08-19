#!/bin/bash

# Make all order lifecycle scripts executable
chmod +x deploy_order_lifecycle.sh
chmod +x fix_database_and_deploy.sh
chmod +x verify_order_lifecycle.sh
chmod +x test_order_lifecycle.py

echo "✅ All scripts are now executable"
echo ""
echo "To fix the database issue and deploy:"
echo "  ./fix_database_and_deploy.sh"
echo ""
echo "To verify everything is working:"
echo "  ./verify_order_lifecycle.sh"
echo ""
echo "To run full tests:"
echo "  python3 test_order_lifecycle.py"