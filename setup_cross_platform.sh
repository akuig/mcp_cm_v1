#!/bin/bash

# 🌍 Cross-Platform Enhanced Catalog Manager Setup
# Automatically detects OS and runs appropriate setup

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_header() {
    echo -e "${BLUE}"
    echo "=============================================="
    echo "🌍 ENHANCED CATALOG MANAGER"
    echo "   Cross-Platform Setup (macOS & Ubuntu)"
    echo "=============================================="
    echo -e "${NC}"
}

detect_platform() {
    echo -e "${YELLOW}🔍 Detecting platform...${NC}"
    
    if [[ "$OSTYPE" == "darwin"* ]]; then
        PLATFORM="macos"
        echo -e "${GREEN}🍎 Detected: macOS${NC}"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if [ -f /etc/lsb-release ] || [ -f /etc/debian_version ]; then
            PLATFORM="ubuntu"
            echo -e "${GREEN}🐧 Detected: Ubuntu/Debian${NC}"
        else
            PLATFORM="linux"
            echo -e "${GREEN}🐧 Detected: Generic Linux${NC}"
        fi
    else
        echo -e "${RED}❌ Unsupported platform: $OSTYPE${NC}"
        echo "Supported platforms:"
        echo "  - macOS (darwin)"
        echo "  - Ubuntu/Debian (linux-gnu)"
        exit 1
    fi
}

run_platform_setup() {
    case $PLATFORM in
        "macos")
            echo -e "${GREEN}🍎 Running macOS setup...${NC}"
            if [ -f "./fix_macos_setup.sh" ]; then
                chmod +x fix_macos_setup.sh
                ./fix_macos_setup.sh
            else
                echo -e "${RED}❌ macOS setup script not found${NC}"
                echo "Expected: ./fix_macos_setup.sh"
                exit 1
            fi
            ;;
        "ubuntu")
            echo -e "${GREEN}🐧 Running Ubuntu setup...${NC}"
            if [ -f "./setup_ubuntu.sh" ]; then
                chmod +x setup_ubuntu.sh
                ./setup_ubuntu.sh
            else
                echo -e "${RED}❌ Ubuntu setup script not found${NC}"
                echo "Expected: ./setup_ubuntu.sh"
                exit 1
            fi
            ;;
        "linux")
            echo -e "${YELLOW}⚠️  Generic Linux detected${NC}"
            echo "This script is optimized for Ubuntu/Debian."
            echo "For other Linux distributions, you may need to:"
            echo "  1. Modify package installation commands"
            echo "  2. Adjust paths and configurations"
            echo ""
            echo "Would you like to try the Ubuntu setup anyway? (y/N)"
            read -r response
            if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
                if [ -f "./setup_ubuntu.sh" ]; then
                    chmod +x setup_ubuntu.sh
                    ./setup_ubuntu.sh
                else
                    echo -e "${RED}❌ Ubuntu setup script not found${NC}"
                    exit 1
                fi
            else
                echo "Setup cancelled. Please manually adapt the Ubuntu script for your distribution."
                exit 1
            fi
            ;;
        *)
            echo -e "${RED}❌ Unknown platform: $PLATFORM${NC}"
            exit 1
            ;;
    esac
}

show_docker_option() {
    echo ""
    echo -e "${BLUE}🐳 Alternative: Docker-First Setup${NC}"
    echo "=============================================="
    echo ""
    echo "For maximum cross-platform compatibility, you can also use"
    echo "the Docker-first approach that works identically on both platforms:"
    echo ""
    echo -e "${GREEN}# Works on both macOS and Ubuntu:${NC}"
    echo "docker-compose -f docker-compose.extended.yml up -d"
    echo "./deploy_final_mcp.sh"
    echo "python test_complete_fixes.py"
    echo ""
    echo "This approach:"
    echo "  ✅ Identical behavior on all platforms"
    echo "  ✅ No dependency management issues"
    echo "  ✅ Consistent performance"
    echo "  ✅ Easy to deploy and scale"
    echo ""
}

show_next_steps() {
    echo ""
    echo -e "${GREEN}🎯 Next Steps:${NC}"
    echo "=============================================="
    echo ""
    
    case $PLATFORM in
        "macos")
            echo "1. ✅ macOS dependencies installed"
            echo "2. 🐳 Start Docker containers:"
            echo "   cd /Users/joe/dev/mcp_cm_v1"
            echo "   docker-compose -f docker-compose.extended.yml up -d"
            echo "3. 🚀 Deploy MCP server:"
            echo "   ./deploy_final_mcp.sh"
            echo "4. 🧪 Test system:"
            echo "   python test_complete_fixes.py"
            ;;
        "ubuntu")
            echo "1. ✅ Ubuntu system configured"
            echo "2. 📋 Copy your enhanced files:"
            echo "   cp /path/to/mcp_server_fixed.py ~/enhanced-catalog-manager/"
            echo "3. 🚀 Start system:"
            echo "   ~/enhanced-catalog-manager/scripts/start.sh"
            echo "4. 🧪 Test endpoints:"
            echo "   curl http://localhost:8080/health"
            ;;
    esac
    
    echo ""
    echo "📚 Documentation available:"
    echo "  - DEMO_QUICK_REFERENCE_CARD.md"
    echo "  - FINAL_DEPLOYMENT_VERIFICATION.md"
    echo "  - comprehensive_demo_scenarios.md"
    echo ""
}

# Main execution
main() {
    print_header
    detect_platform
    
    echo ""
    echo "Platform-specific setup will now begin..."
    echo "This will install all dependencies and configure the Enhanced Catalog Manager."
    echo ""
    echo "Continue with $PLATFORM setup? (Y/n)"
    read -r response
    
    if [[ "$response" =~ ^([nN][oO]|[nN])$ ]]; then
        echo "Setup cancelled."
        show_docker_option
        exit 0
    fi
    
    run_platform_setup
    show_next_steps
    show_docker_option
    
    echo -e "${GREEN}🏆 Cross-platform setup completed!${NC}"
}

# Check for required files
if [ ! -f "./docker-compose.extended.yml" ]; then
    echo -e "${RED}❌ This doesn't appear to be the Enhanced Catalog Manager directory${NC}"
    echo "Please run this script from the project root directory containing:"
    echo "  - docker-compose.extended.yml"
    echo "  - fix_macos_setup.sh (for macOS)"
    echo "  - setup_ubuntu.sh (for Ubuntu)"
    exit 1
fi

# Run the setup
main "$@"
