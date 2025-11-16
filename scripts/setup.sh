#!/bin/bash
#
# MirrorDNA Setup Script
#
# Automated setup for development environment
# Usage: ./scripts/setup.sh
#

set -e

echo "========================================="
echo "MirrorDNA Protocol - Setup Script"
echo "========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.8"

if python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)" 2>/dev/null; then
    echo -e "${GREEN}✓${NC} Python $python_version (>= 3.8 required)"
else
    echo -e "${RED}✗${NC} Python 3.8 or higher required. Found: $python_version"
    exit 1
fi

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo -e "${YELLOW}!${NC} Virtual environment already exists"
    read -p "Remove and recreate? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf venv
    else
        echo "Using existing virtual environment"
    fi
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo -e "${GREEN}✓${NC} Virtual environment created"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1
echo -e "${GREEN}✓${NC} pip upgraded"

# Install package in editable mode with dev dependencies
echo "Installing MirrorDNA in editable mode..."
pip install -e ".[dev]" > /dev/null 2>&1
echo -e "${GREEN}✓${NC} MirrorDNA installed"

# Verify installation
echo ""
echo "Verifying installation..."
if command -v mirrordna &> /dev/null; then
    echo -e "${GREEN}✓${NC} CLI tool installed: $(which mirrordna)"
    mirrordna --version
else
    echo -e "${RED}✗${NC} CLI tool not found in PATH"
    exit 1
fi

# Run tests to verify everything works
echo ""
echo "Running tests..."
if pytest tests/ -v --tb=short; then
    echo -e "${GREEN}✓${NC} All tests passed"
else
    echo -e "${RED}✗${NC} Some tests failed"
    exit 1
fi

# Create default data directory
echo ""
echo "Creating default data directory..."
mkdir -p ~/.mirrordna/data
mkdir -p ~/.mirrordna/logs
echo -e "${GREEN}✓${NC} Data directories created"

echo ""
echo "========================================="
echo -e "${GREEN}Setup completed successfully!${NC}"
echo "========================================="
echo ""
echo "Next steps:"
echo "  1. Activate the virtual environment: source venv/bin/activate"
echo "  2. Try the CLI: mirrordna --help"
echo "  3. Run quickstart: ./scripts/quickstart.sh"
echo "  4. Run tests: pytest tests/ -v"
echo ""
echo "Documentation: ./docs/index.md"
echo "Examples: ./examples/"
echo ""
