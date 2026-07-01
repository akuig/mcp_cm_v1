#!/bin/bash
# Make all product_service_links fix scripts executable

chmod +x docker_fix_links.sh
chmod +x quick_docker_fix.sh
chmod +x localhost_fix_links.sh
chmod +x apply_product_service_links.sh
chmod +x quick_fix_links.sh

echo "✅ All scripts are now executable!"
echo ""
echo "Recommended command to run:"
echo "  ./docker_fix_links.sh"
echo ""
echo "Or for quickest execution:"
echo "  ./quick_docker_fix.sh"
