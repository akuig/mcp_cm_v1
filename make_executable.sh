#!/bin/bash
# Commands to make scripts executable and run the demo

chmod +x setup_fault_management.sh
chmod +x run_fault_demo.sh
chmod +x test_fault_quick.sh

echo "Scripts are now executable!"
echo ""
echo "To run the complete fault management demo:"
echo "  ./run_fault_demo.sh"
echo ""
echo "Or manually:"
echo "  1. Start services: docker-compose -f docker-compose-with-fault.yml up -d"
echo "  2. Wait 20 seconds for initialization"
echo "  3. Run demo: python test_fault_management.py"
