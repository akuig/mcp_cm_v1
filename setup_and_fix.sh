#!/bin/bash
# Complete setup and run script for fault management demo

echo "🚀 Telepath AI Fault Management Demo Setup"
echo "=========================================="
echo ""

# Make all scripts executable
chmod +x fix_mcp_server.sh
chmod +x run_fault_demo.sh
chmod +x test_fault_quick.sh
chmod +x check_services.py
chmod +x test_fault_management.py

# Run the fix
./fix_mcp_server.sh

echo ""
echo "Setup complete! To run the demo:"
echo "  python test_fault_management.py"
echo ""
echo "Or use the automated runner:"
echo "  ./run_fault_demo.sh"
