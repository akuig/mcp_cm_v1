#!/bin/bash
echo "🔧 Making all setup scripts executable..."
chmod +x *.sh 2>/dev/null || true
chmod +x scripts/*.sh 2>/dev/null || true
echo "✅ All scripts are now executable"
echo ""
echo "🚀 Available setup options:"
echo "  ./fix_macos_setup.sh          - Fix current macOS issues"
echo "  ./setup_ubuntu.sh             - Complete Ubuntu setup"  
echo "  ./setup_cross_platform.sh     - Auto-detect and setup"
echo ""
echo "🐳 Docker option (works on both):"
echo "  docker-compose -f docker-compose.extended.yml up -d"
echo ""
