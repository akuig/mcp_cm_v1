#!/bin/bash
# Demo Reset Wrapper Script
# Quick and easy way to reset demo database

set -e  # Exit on any error

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="$SCRIPT_DIR/demo_reset.py"
LOG_FILE="$SCRIPT_DIR/logs/demo_reset_$(date +%Y%m%d_%H%M%S).log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🎭 Telepath AI - Demo Reset Utility${NC}"
echo "=================================================="

# Create logs directory if it doesn't exist
mkdir -p "$SCRIPT_DIR/logs"

# Function to show usage
show_usage() {
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  --dry-run          Show what would be reset without making changes"
    echo "  --customer-id ID   Specify customer ID to reset (default: 8452934)"
    echo "  --url URL          Specify catalog manager URL"
    echo "  --help             Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                 # Reset demo data"
    echo "  $0 --dry-run       # Preview what would be reset"
    echo "  $0 --customer-id 123456  # Reset specific customer"
}

# Parse arguments
DRY_RUN=""
CUSTOMER_ID=""
URL=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run)
            DRY_RUN="--dry-run"
            shift
            ;;
        --customer-id)
            CUSTOMER_ID="--customer-id $2"
            shift 2
            ;;
        --url)
            URL="--url $2"
            shift 2
            ;;
        --help|-h)
            show_usage
            exit 0
            ;;
        *)
            echo -e "${RED}❌ Unknown option: $1${NC}"
            show_usage
            exit 1
            ;;
    esac
done

# Check if Python script exists
if [[ ! -f "$PYTHON_SCRIPT" ]]; then
    echo -e "${RED}❌ Python script not found: $PYTHON_SCRIPT${NC}"
    echo "Please ensure demo_reset.py is in the same directory as this script"
    exit 1
fi

# Confirmation (skip for dry run)
if [[ -z "$DRY_RUN" ]]; then
    echo -e "${YELLOW}⚠️  This will reset demo database and delete test data!${NC}"
    echo -n "Are you sure you want to continue? (y/N): "
    read -r confirmation
    
    if [[ ! "$confirmation" =~ ^[Yy]$ ]]; then
        echo -e "${BLUE}ℹ️  Reset cancelled by user${NC}"
        exit 0
    fi
    echo ""
fi

# Run the Python script
echo -e "${BLUE}🚀 Starting demo reset...${NC}"
echo "Log file: $LOG_FILE"
echo ""

# Build the command
PYTHON_CMD="python3 $PYTHON_SCRIPT $DRY_RUN $CUSTOMER_ID $URL"

# Run with logging
if $PYTHON_CMD 2>&1 | tee "$LOG_FILE"; then
    if [[ -z "$DRY_RUN" ]]; then
        echo ""
        echo -e "${GREEN}✅ Demo reset completed successfully!${NC}"
        echo -e "${GREEN}🎯 System ready for fresh demonstration${NC}"
    else
        echo ""
        echo -e "${BLUE}ℹ️  Dry run completed - no changes made${NC}"
    fi
else
    echo ""
    echo -e "${RED}❌ Demo reset failed!${NC}"
    echo -e "${YELLOW}Check the log file for details: $LOG_FILE${NC}"
    exit 1
fi

# Optional: Clean up old log files (keep last 10)
find "$SCRIPT_DIR/logs" -name "demo_reset_*.log" -type f | sort | head -n -10 | xargs -r rm

echo ""
echo -e "${BLUE}📋 Reset complete - log saved to: $LOG_FILE${NC}"
