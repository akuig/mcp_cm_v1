#!/bin/bash

# Make deployment scripts executable
chmod +x deploy_order_lifecycle.sh
chmod +x test_order_lifecycle.py

echo "✅ Scripts are now executable"
echo ""
echo "To deploy the new order lifecycle management tools:"
echo "  ./deploy_order_lifecycle.sh"
echo ""
echo "To test the new tools:"
echo "  python3 test_order_lifecycle.py"