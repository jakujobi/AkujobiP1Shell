"""
Main shell module - REPL loop and entry point.

This module contains the main command-line interface and REPL loop
for the AkujobiP1Shell.
"""

import os
import sys
import signal

# TODO: Import config, parser, builtins, executor modules once implemented


def cli() -> int:
    """
    Main entry point for the shell application.

    Returns:
        Exit code (0 for success)
    """
    # TODO: Implement main entry point
    print("AkujobiP1Shell - Phase 1 Setup Complete")
    print("Full implementation coming in Phase 2...")
    return 0


def run_shell(config: dict) -> int:
    """
    Run the main REPL loop.

    Args:
        config: Configuration dictionary

    Returns:
        Exit code
    """
    # TODO: Implement REPL loop
    pass


def setup_signal_handlers() -> None:
    """
    Set up signal handlers for SIGINT (Ctrl+C).
    """
    # TODO: Implement signal handler setup
    pass


def sigint_handler(signum: int, frame) -> None:
    """
    Handle SIGINT (Ctrl+C) by showing new prompt.

    Args:
        signum: Signal number
        frame: Current stack frame
    """
    # TODO: Implement SIGINT handler
    pass

