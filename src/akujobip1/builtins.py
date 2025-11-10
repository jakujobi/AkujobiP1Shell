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
    """
    Exit the shell.

    Prints configured exit message and returns -1 to signal shell termination.
    """

    def execute(self, args: List[str], config: Dict[str, Any]) -> int:
        """
        Execute exit command.

        Args:
            args: Command arguments (only args[0]='exit' expected)
            config: Configuration dictionary

        Returns:
            -1 to signal shell to exit

        Example:
            >>> config = {'exit': {'message': 'Goodbye!'}}
            >>> cmd = ExitCommand()
            >>> cmd.execute(['exit'], config)
            Goodbye!
            -1
        """
        # Get exit message from config
        # Handle None values in config (malformed config)
        exit_config = config.get("exit", {})
        if exit_config is None:
            exit_config = {}
        message = exit_config.get("message", "Bye!")
        print(message)

        # Return -1 to signal shell to exit
        return -1


class CdCommand(BuiltinCommand):
    """
    Change directory.

    Supports:
    - cd (no args) - change to home directory
    - cd <path> - change to specified directory
    - cd - - change to previous directory (OLDPWD)
    """

    # Class variable to track previous directory for cd -
    _previous_directory: Optional[str] = None

    def execute(self, args: List[str], config: Dict[str, Any]) -> int:
        """
        Execute cd command.

        Args:
            args: Command arguments (args[0]='cd', args[1]=target or missing)
            config: Configuration dictionary

        Returns:
            0 on success, 1 on error

        Example:
            >>> config = {'builtins': {'cd': {'show_pwd_after': False}}}
            >>> cmd = CdCommand()
            >>> cmd.execute(['cd', '/tmp'], config)
            0
            >>> cmd.execute(['cd', '-'], config)
            0
        """
        # Determine target directory
        if len(args) == 1:
            # No arguments - go to home directory
            target = os.path.expanduser("~")
        elif args[1] == "-":
            # cd - go to previous directory
            if self._previous_directory is None:
                print("cd: OLDPWD not set", file=sys.stderr)
                return 1
            target = self._previous_directory
        else:
            # cd <path> - go to specified directory
            target = args[1]

        # Save current directory before changing
        try:
            current = os.getcwd()
        except OSError:
            # Current directory no longer exists
            current = None

        # Try to change directory
        try:
            os.chdir(target)
        except FileNotFoundError:
            print(f"cd: {target}: No such file or directory", file=sys.stderr)
            return 1
        except NotADirectoryError:
            print(f"cd: {target}: Not a directory", file=sys.stderr)
            return 1
        except PermissionError:
            print(f"cd: {target}: Permission denied", file=sys.stderr)
            return 1
        except OSError as e:
            # Catch any other OS errors
            print(f"cd: {target}: {e}", file=sys.stderr)
            return 1

        # Update previous directory
        if current:
            CdCommand._previous_directory = current

        # Optionally show pwd after cd
        # Handle None values in config (malformed config)
        builtins_config = config.get("builtins", {})
        if builtins_config is None:
            builtins_config = {}
        cd_config = builtins_config.get("cd", {})
        if cd_config is None:
            cd_config = {}
        if cd_config.get("show_pwd_after", False):
            print(os.getcwd())

        return 0


class PwdCommand(BuiltinCommand):
    """
    Print working directory.

    Displays the absolute path of the current working directory.
    """

    def execute(self, args: List[str], config: Dict[str, Any]) -> int:
        """
        Execute pwd command.

        Args:
            args: Command arguments (only args[0]='pwd' expected)
            config: Configuration dictionary

        Returns:
            0 on success, 1 on error

        Example:
            >>> cmd = PwdCommand()
            >>> cmd.execute(['pwd'], {})
            /home/user
            0
        """
        try:
            print(os.getcwd())
            return 0
        except OSError as e:
            # Handle edge case where current directory was deleted
            print(f"pwd: {e}", file=sys.stderr)
            return 1


class HelpCommand(BuiltinCommand):
    """
    Show help information.

    Displays list of available built-in commands with brief usage info.
    """

    def execute(self, args: List[str], config: Dict[str, Any]) -> int:
        """
        Execute help command.

        Args:
            args: Command arguments (only args[0]='help' expected)
            config: Configuration dictionary

        Returns:
            0 (always succeeds)

        Example:
            >>> cmd = HelpCommand()
            >>> cmd.execute(['help'], {})
            Built-in commands:
              exit       Exit the shell
              cd [dir]   Change directory (cd - for previous, cd for home)
              pwd        Print working directory
              help       Show this help message
            0
        """
        print("Built-in commands:")
        print("  exit       Exit the shell")
        print("  cd [dir]   Change directory (cd - for previous, cd for home)")
        print("  pwd        Print working directory")
        print("  help       Show this help message")
        return 0


# Built-in command registry
BUILTINS: Dict[str, BuiltinCommand] = {
    "exit": ExitCommand(),
    "cd": CdCommand(),
    "pwd": PwdCommand(),
    "help": HelpCommand(),
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
