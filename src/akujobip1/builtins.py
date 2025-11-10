"""
Built-in commands module.

This module implements shell built-in commands that are executed
directly by the shell without forking a new process.
"""

import os
import sys
from typing import List, Dict, Any, Optional


class BuiltinCommand:
    """Base class for built-in commands."""

    def execute(self, args: List[str], config: Dict[str, Any]) -> int:
        """
        Execute the built-in command.

        Args:
            args: Command arguments (including command name at args[0])
            config: Configuration dictionary

        Returns:
            Exit code (0 for success, non-zero for error)
        """
        raise NotImplementedError


class ExitCommand(BuiltinCommand):
    """Exit the shell."""

    def execute(self, args: List[str], config: Dict[str, Any]) -> int:
        # TODO: Implement exit command
        pass


class CdCommand(BuiltinCommand):
    """Change directory."""

    def execute(self, args: List[str], config: Dict[str, Any]) -> int:
        # TODO: Implement cd command
        pass


class PwdCommand(BuiltinCommand):
    """Print working directory."""

    def execute(self, args: List[str], config: Dict[str, Any]) -> int:
        # TODO: Implement pwd command
        pass


class HelpCommand(BuiltinCommand):
    """Show help information."""

    def execute(self, args: List[str], config: Dict[str, Any]) -> int:
        # TODO: Implement help command
        pass


# Built-in command registry
BUILTINS: Dict[str, BuiltinCommand] = {
    'exit': ExitCommand(),
    'cd': CdCommand(),
    'pwd': PwdCommand(),
    'help': HelpCommand()
}


def get_builtin(name: str) -> Optional[BuiltinCommand]:
    """
    Get built-in command by name.

    Args:
        name: Command name

    Returns:
        BuiltinCommand instance or None if not found
    """
    return BUILTINS.get(name)

