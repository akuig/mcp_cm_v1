#!/bin/bash
# Make all standardization scripts executable

chmod +x execute_standardization.sh
chmod +x quick_fix_server2.sh
chmod +x test_standardization.sh

echo "✅ All standardization scripts are now executable!"
echo ""
echo "Available commands:"
echo "  ./execute_standardization.sh  - Complete standardization wizard"
echo "  ./quick_fix_server2.sh        - Quick fix for Server 2 critical issue"
echo "  ./test_standardization.sh     - Verify catalog after standardization"
echo ""
echo "SQL scripts (use with Docker):"
echo "  fix_server2_critical.sql"
echo "  upgrade_server1_to_match_server2.sql"
echo "  standardize_both_servers.sql"
echo "  optional_deprecate_unused_specs.sql"
echo ""
echo "Documentation:"
echo "  CATALOG_STANDARDIZATION_GUIDE.md"
echo ""
