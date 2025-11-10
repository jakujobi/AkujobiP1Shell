#!/bin/bash
# Quick activation script for AkujobiP1Shell virtual environment

if [ ! -f "venv/bin/activate" ]; then
    echo "Virtual environment not found. Running setup..."
    ./setup.sh
else
    source venv/bin/activate
    echo "Virtual environment activated!"
    echo "Run 'akujobip1' to start the shell"
fi

