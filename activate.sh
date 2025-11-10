#!/bin/bash
# AkujobiP1Shell environment setup and activation script
# This script handles both setup and activation in one command

set -e  # Exit on error

# Check if we're in the project root directory
if [ ! -f "pyproject.toml" ]; then
    echo "Error: Please run this script from the project root directory"
    echo "       (the directory containing pyproject.toml)"
    exit 1
fi

# If virtual environment doesn't exist, set it up
if [ ! -f "venv/bin/activate" ]; then
    echo "=========================================="
    echo "AkujobiP1Shell Setup"
    echo "=========================================="
    echo ""

    # Check if python3-venv is installed
    echo "[1/7] Checking python3-venv..."
    if ! python3 -m venv --help > /dev/null 2>&1; then
        echo ""
        echo "✗ ERROR: python3-venv is not installed."
        echo ""
        echo "You need to install it with sudo (administrator privileges):"
        echo ""
        echo "  sudo apt install python3-venv"
        echo ""
        echo "Or for Python 3.12 specifically:"
        echo ""
        echo "  sudo apt install python3.12-venv"
        echo ""
        echo "After installing, run this script again:"
        echo "  ./activate.sh"
        echo ""
        exit 1
    fi

    # Test if venv can actually be created (check ensurepip)
    echo "  ✓ python3-venv command is available"
    echo "  Testing virtual environment creation..."
    TEMP_VENV_TEST=$(mktemp -d)
    if python3 -m venv "$TEMP_VENV_TEST" 2>/dev/null && [ -f "$TEMP_VENV_TEST/bin/activate" ]; then
        rm -rf "$TEMP_VENV_TEST"
        echo "  ✓ Virtual environment creation test passed"
    else
        rm -rf "$TEMP_VENV_TEST" 2>/dev/null || true
        echo ""
        echo "✗ ERROR: Virtual environment creation test failed."
        echo ""
        echo "This usually means python3-venv is not fully installed."
        echo "You need to install it with sudo:"
        echo ""
        echo "  sudo apt install python3-venv"
        echo ""
        echo "Or for Python 3.12 specifically:"
        echo ""
        echo "  sudo apt install python3.12-venv"
        echo ""
        echo "After installing, run this script again:"
        echo "  ./activate.sh"
        echo ""
        exit 1
    fi
    echo ""

    # Clean up incomplete venv if it exists
    if [ -d "venv" ] && [ ! -f "venv/bin/activate" ]; then
        echo "[2/7] Cleaning up incomplete virtual environment..."
        rm -rf venv
        echo "  ✓ Cleaned up"
        echo ""
    fi

    # Create virtual environment
    echo "[2/7] Creating virtual environment..."
    if [ -d "venv" ] && [ -f "venv/bin/activate" ]; then
        echo "  ✓ Virtual environment already exists"
    else
        # Try to create venv and capture any errors
        if python3 -m venv venv 2>&1; then
            # Verify it was actually created
            if [ -f "venv/bin/activate" ]; then
                echo "  ✓ Virtual environment created successfully"
            else
                echo "  ✗ ERROR: Virtual environment creation failed"
                echo "  The venv directory was created but is incomplete."
                echo ""
                echo "  You need to install python3-venv with sudo:"
                echo "    sudo apt install python3-venv"
                echo ""
                rm -rf venv
                exit 1
            fi
        else
            echo "  ✗ ERROR: Failed to create virtual environment"
            echo ""
            echo "  This usually means python3-venv is not fully installed."
            echo "  You need to install it with sudo:"
            echo ""
            echo "    sudo apt install python3-venv"
            echo ""
            echo "  Or for Python 3.12 specifically:"
            echo ""
            echo "    sudo apt install python3.12-venv"
            echo ""
            rm -rf venv 2>/dev/null || true
            exit 1
        fi
    fi
    echo ""

    # Activate virtual environment
    echo "[3/7] Activating virtual environment..."
    if [ ! -f "venv/bin/activate" ]; then
        echo "  ✗ ERROR: Cannot activate virtual environment"
        echo "  venv/bin/activate not found"
        exit 1
    fi
    source venv/bin/activate
    echo "  ✓ Virtual environment activated"
    echo ""

    # Upgrade pip (if available)
    echo "[4/7] Checking pip..."
    if command -v pip >/dev/null 2>&1; then
        echo "  Upgrading pip..."
        pip install --upgrade pip --quiet
        echo "  ✓ pip upgraded"
    else
        echo "  ✓ pip not available in current environment (will use venv pip)"
    fi
    echo ""

    # Install package in editable mode
    echo "[5/7] Installing AkujobiP1Shell..."
    pip install -e . --quiet
    echo "  ✓ Package installed"
    echo ""

    # Install development dependencies
    echo "[6/7] Installing development dependencies..."
    pip install -e ".[dev]" --quiet
    echo "  ✓ Development dependencies installed"
    echo ""

    # Test installation
    echo "[7/7] Testing installation..."
    if command -v akujobip1 >/dev/null 2>&1; then
        echo "  ✓ akujobip1 command is available"
        # Test if the command actually runs and returns 0
        if akujobip1 >/dev/null 2>&1; then
            echo "  ✓ akujobip1 command executes successfully"
        else
            EXIT_CODE=$?
            if [ $EXIT_CODE -eq 0 ]; then
                echo "  ✓ akujobip1 command executes successfully"
            else
                echo "  ✗ Warning: akujobip1 command returned exit code $EXIT_CODE"
            fi
        fi
        # Test if Python module import works
        if python -c "from akujobip1.shell import cli" 2>/dev/null; then
            echo "  ✓ Python module imports successfully"
        else
            echo "  ✗ Warning: Python module import failed"
        fi
    else
        echo "  ✗ ERROR: akujobip1 command not found"
        echo "  Installation may have failed"
        exit 1
    fi
    echo ""

    echo "=========================================="
    echo "Setup Complete!"
    echo "=========================================="
    echo ""

else
    # Virtual environment exists, just activate it
    source venv/bin/activate
    echo "Virtual environment activated!"
fi

# Final instructions
echo "To run the shell:"
echo "  akujobip1"
echo ""
echo "Or:"
echo "  python -m akujobip1"
echo ""

