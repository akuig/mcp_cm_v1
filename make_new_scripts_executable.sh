#!/bin/bash
# Make all new scripts executable

chmod +x fix_mcp_asyncio.sh
chmod +x final_fix_asyncio.sh
chmod +x test_fault_manager_local.py

echo "✅ All scripts are now executable!"
echo ""
echo "To fix the AsyncIO error and run the demo:"
echo "  ./final_fix_asyncio.sh"
echo "  python test_fault_management.py"
