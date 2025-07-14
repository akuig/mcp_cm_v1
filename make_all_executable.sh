#!/bin/bash
# Make all scripts executable

echo "Making all scripts executable..."

chmod +x diagnose_fault_manager.sh
chmod +x fix_fault_manager.sh
chmod +x test_fault_manager_local.py
chmod +x complete_fix.sh
chmod +x quick_start_workaround.sh

echo "✅ All scripts are now executable!"
echo ""
echo "Run one of these to fix the issue:"
echo "  ./complete_fix.sh         (Full rebuild - recommended)"
echo "  ./quick_start_workaround.sh  (Quick start without health checks)"
