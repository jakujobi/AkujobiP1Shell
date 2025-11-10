"""
Command parsing module.

This module handles parsing user input into command arguments,
including support for quoted strings and wildcard expansion.
"""

import shlex
import glob
from typing import List


def parse_command(command_line: str) -> List[str]:
    """
    Parse a command line string into a list of arguments.

    Uses shlex.split() for proper handling of quoted arguments.

    Args:
        command_line: Raw command line input from user

    Returns:
        List of parsed arguments (empty list if input is empty/whitespace)
    """
    # TODO: Implement command parsing
    raise NotImplementedError


def expand_wildcards(args: List[str]) -> List[str]:
    """
    Expand wildcard patterns in arguments using glob.

    Args:
        args: List of command arguments

    Returns:
        List of arguments with wildcards expanded
    """
    # TODO: Implement wildcard expansion
    raise NotImplementedError

