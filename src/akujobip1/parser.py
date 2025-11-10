"""
Command parsing module.

This module handles parsing user input into command arguments,
including support for quoted strings and wildcard expansion.
"""

import shlex
import glob
from typing import List, Dict, Any


def parse_command(command_line: str, config: Dict[str, Any]) -> List[str]:
    """
    Parse a command line string into a list of arguments.

    Uses shlex.split() for proper handling of quoted arguments,
    then expands wildcards if enabled in configuration.

    Args:
        command_line: Raw command line input from user
        config: Configuration dictionary containing glob settings

    Returns:
        List of parsed arguments (empty list if input is empty/whitespace)

    Examples:
        >>> config = {'glob': {'enabled': True}}
        >>> parse_command('ls -la', config)
        ['ls', '-la']
        >>> parse_command('echo "hello world"', config)
        ['echo', 'hello world']
        >>> parse_command('  ', config)
        []
        >>> parse_command('ls *.txt', config)  # Expands if files exist
        ['ls', 'file1.txt', 'file2.txt']
    """
    # Handle empty or whitespace-only input
    if not command_line or not command_line.strip():
        return []

    try:
        # Use shlex to properly parse quoted arguments
        # This handles both single and double quotes, plus escapes
        args = shlex.split(command_line)
    except ValueError as e:
        # shlex can raise ValueError for unclosed quotes
        # Print error and return empty list (graceful degradation)
        print(f"Parse error: {e}", file=__import__("sys").stderr)
        return []

    # If no arguments after parsing, return empty list
    if not args:
        return []

    # Expand wildcards if enabled in config
    # Handle None values in config (malformed config)
    glob_config = config.get("glob", {})
    if glob_config is None:
        glob_config = {}
    if glob_config.get("enabled", True):
        args = expand_wildcards(args, config)

    return args


def expand_wildcards(args: List[str], config: Dict[str, Any]) -> List[str]:
    """
    Expand wildcard patterns in arguments using glob.

    Only expands arguments that contain wildcard characters (*, ?, [).
    If no matches are found, the literal argument is kept.
    Respects the glob.enabled configuration setting.

    Args:
        args: List of command arguments (may contain wildcards)
        config: Configuration dictionary containing glob settings

    Returns:
        List of arguments with wildcards expanded to matching files

    Examples:
        >>> config = {'glob': {'enabled': True}}
        >>> expand_wildcards(['ls', '*.txt'], config)
        ['ls', 'file1.txt', 'file2.txt']  # If files exist
        >>> expand_wildcards(['echo', 'no*match'], config)
        ['echo', 'no*match']  # No matches, keep literal
        >>> expand_wildcards(['cp', 'file?.txt', 'dest/'], config)
        ['cp', 'file1.txt', 'file2.txt', 'dest/']
    """
    # Check if glob expansion is disabled
    # Handle None values in config (malformed config)
    glob_config = config.get("glob", {})
    if glob_config is None:
        glob_config = {}
    if not glob_config.get("enabled", True):
        return args

    expanded_args = []

    for arg in args:
        # Only try to expand if the argument contains wildcard characters
        if _contains_wildcard(arg):
            # Try to expand the wildcard
            matches = sorted(glob.glob(arg))

            # If matches found, add them; otherwise keep the literal
            if matches:
                expanded_args.extend(matches)
            else:
                # No matches - keep the literal argument
                expanded_args.append(arg)
        else:
            # Not a wildcard, keep as-is
            expanded_args.append(arg)

    return expanded_args


def _contains_wildcard(arg: str) -> bool:
    """
    Check if an argument contains wildcard characters.

    Args:
        arg: Argument string to check

    Returns:
        True if the argument contains *, ?, or [ characters

    Examples:
        >>> _contains_wildcard('*.txt')
        True
        >>> _contains_wildcard('file?.py')
        True
        >>> _contains_wildcard('test[123].log')
        True
        >>> _contains_wildcard('regular_file.txt')
        False
    """
    return "*" in arg or "?" in arg or "[" in arg
