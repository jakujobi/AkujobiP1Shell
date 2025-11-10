"""
Main entry point for running akujobip1 as a module.

This file allows the shell to be executed with:
    python -m akujobip1

It simply calls the cli() function from shell.py.
"""

import sys
from akujobip1.shell import cli

if __name__ == "__main__":
    sys.exit(cli())
