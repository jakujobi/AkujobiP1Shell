#!/bin/bash
# Quick Demo Script for AkujobiP1Shell
# Run this to perform a quick demonstration of all features
# Author: John Akujobi

echo "=========================================="
echo " AkujobiP1Shell - Quick Demo"
echo " Version: 1.0.0"
echo "=========================================="
echo ""

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ] || [ ! -d "src/akujobip1" ]; then
    echo "Error: Please run this script from the AkujobiP1Shell directory"
    exit 1
fi

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "Error: Virtual environment not found. Run ./activate.sh first"
    exit 1
fi

# Activate venv
source venv/bin/activate

echo "✓ Virtual environment activated"
echo ""

# Run tests quickly
echo "Running tests..."
pytest -q
if [ $? -ne 0 ]; then
    echo "Tests failed! Fix before demo."
    exit 1
fi
echo "✓ All 229 tests passing"
echo ""

# Check linting
echo "Checking code quality..."
ruff check src/ > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✓ No linting errors"
else
    echo "⚠ Linting warnings found"
fi
echo ""

# Create demo config
echo "Creating demo configuration..."
cat > /tmp/demo_config.yaml << 'EOF'
execution:
  show_exit_codes: "always"
  exit_code_format: "[Exit: {code}]"
debug:
  show_fork_pids: true
EOF
echo "✓ Demo config created"
echo ""

echo "=========================================="
echo " Demo Commands Ready!"
echo "=========================================="
echo ""
echo "To start demo, run:"
echo ""
echo "    akujobip1"
echo ""
echo "Or with debug mode:"
echo ""
echo "    AKUJOBIP1_CONFIG=/tmp/demo_config.yaml akujobip1"
echo ""
echo "Try these commands in the shell:"
echo ""
echo "  pwd              # Show current directory"
echo "  ls               # List files"
echo "  cd /tmp && cd -  # Change directory and back"
echo "  ls *.py          # Wildcard expansion"
echo "  echo \"test\"     # Quote handling"
echo "  badcommand       # Error handling"
echo "  sleep 5          # Then press Ctrl+C"
echo "  help             # Show built-ins"
echo "  exit             # Exit shell"
echo ""
echo "See docs/DEMO_GUIDE.md for complete demo script"
echo ""
echo "Ready to demo!"

