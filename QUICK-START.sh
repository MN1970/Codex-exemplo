#!/bin/bash
# QUICK-START.sh — Setup rápido para sp_healthcheck.py
#
# Uso:
#   bash QUICK-START.sh          # Verify setup
#   bash QUICK-START.sh --setup  # Interactive setup
#   bash QUICK-START.sh --test   # Run tests

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HEALTHCHECK_SCRIPT="$SCRIPT_DIR/scripts/sp_healthcheck.py"
TEST_SCRIPT="$SCRIPT_DIR/scripts/test_healthcheck.py"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Manta M365 Healthcheck v2 Quick Start ===${NC}\n"

# Function to print section headers
print_header() {
    echo -e "${YELLOW}→ $1${NC}"
}

# Function to print success
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

# Function to print error
print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Check Python
print_header "Checking Python..."
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 not found"
    exit 1
fi
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
print_success "Python $PYTHON_VERSION found"

# Check requests library
print_header "Checking requests library..."
if ! python3 -c "import requests" 2>/dev/null; then
    print_error "requests library not found"
    echo "Install with: pip install requests"
    exit 1
fi
print_success "requests library installed"

# Check script syntax
print_header "Checking script syntax..."
if ! python3 -m py_compile "$HEALTHCHECK_SCRIPT" 2>/dev/null; then
    print_error "Script syntax error"
    exit 1
fi
print_success "Script syntax is valid"

# Check test file
print_header "Checking test file..."
if [ ! -f "$TEST_SCRIPT" ]; then
    print_error "Test script not found: $TEST_SCRIPT"
    exit 1
fi
print_success "Test script found"

# Check environment variables
print_header "Checking environment variables..."
REQUIRED_VARS=("AZURE_CLIENT_ID" "AZURE_CLIENT_SECRET" "SHAREPOINT_TENANT_ID")
MISSING_VARS=()

for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var}" ]; then
        MISSING_VARS+=("$var")
    fi
done

if [ ${#MISSING_VARS[@]} -gt 0 ]; then
    print_error "Missing environment variables:"
    for var in "${MISSING_VARS[@]}"; do
        echo "  - $var"
    done
    echo ""
    if [ "$1" = "--setup" ]; then
        echo "Setting up environment variables..."
        read -p "Enter AZURE_CLIENT_ID: " AZURE_CLIENT_ID
        read -p "Enter AZURE_CLIENT_SECRET: " AZURE_CLIENT_SECRET
        read -p "Enter SHAREPOINT_TENANT_ID: " SHAREPOINT_TENANT_ID

        # Create .env file
        cat > "$SCRIPT_DIR/.env.healthcheck" << EOF
export AZURE_CLIENT_ID="$AZURE_CLIENT_ID"
export AZURE_CLIENT_SECRET="$AZURE_CLIENT_SECRET"
export SHAREPOINT_TENANT_ID="$SHAREPOINT_TENANT_ID"
export SHAREPOINT_TENANT_NAME="mantaassociados"
export SHAREPOINT_SITE_NAME="manta-maestro"
export AZURE_KEYVAULT_NAME="manta-maestro-vault"
export AZURE_SECRET_NAME="manta-maestro-credentials"
EOF
        print_success "Environment variables saved to .env.healthcheck"
        echo ""
        echo "To use these variables, run:"
        echo "  source $SCRIPT_DIR/.env.healthcheck"
    else
        echo "Use: bash QUICK-START.sh --setup"
        echo ""
    fi
else
    print_success "All required environment variables set"
fi

# Display summary
echo ""
print_header "Setup Summary"
echo "Python: $(python3 --version 2>&1)"
echo "Requests: $(python3 -c 'import requests; print(requests.__version__)')"
echo "Script: $HEALTHCHECK_SCRIPT"
echo "Tests: $TEST_SCRIPT"

# Handle flags
case "$1" in
    --test)
        echo ""
        print_header "Running unit tests..."
        python3 "$TEST_SCRIPT"
        ;;
    --run)
        echo ""
        print_header "Running healthcheck (dry-run mode)..."
        python3 "$HEALTHCHECK_SCRIPT" --dry-run --verbose
        ;;
    --run-full)
        echo ""
        print_header "Running healthcheck (full mode with SP write)..."
        if [ ${#MISSING_VARS[@]} -gt 0 ]; then
            print_error "Cannot run full test without credentials"
            exit 1
        fi
        python3 "$HEALTHCHECK_SCRIPT" --verbose
        ;;
    --help)
        echo ""
        echo "Usage: bash QUICK-START.sh [option]"
        echo ""
        echo "Options:"
        echo "  (none)         Verify setup"
        echo "  --setup        Interactive environment setup"
        echo "  --test         Run unit tests"
        echo "  --run          Run healthcheck (dry-run, no SP write)"
        echo "  --run-full     Run healthcheck (full test with SP write)"
        echo "  --help         Show this help"
        exit 0
        ;;
    *)
        echo ""
        print_success "Setup verification complete!"
        echo ""
        echo "Next steps:"
        if [ ${#MISSING_VARS[@]} -gt 0 ]; then
            echo "1. Configure credentials:  bash QUICK-START.sh --setup"
        else
            echo "1. Credentials configured ✓"
        fi
        echo "2. Run unit tests:          bash QUICK-START.sh --test"
        echo "3. Dry-run healthcheck:     bash QUICK-START.sh --run"
        if [ ${#MISSING_VARS[@]} -eq 0 ]; then
            echo "4. Full healthcheck:        bash QUICK-START.sh --run-full"
        fi
        echo ""
        echo "For more details, see:"
        echo "  - HEALTHCHECK-SETUP.md"
        echo "  - IMPLEMENTATION-SUMMARY.md"
        ;;
esac

echo ""
