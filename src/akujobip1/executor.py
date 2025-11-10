"""
External command executor module.

This module handles execution of external commands using POSIX
system calls: fork(), execvp(), and waitpid().

POSIX References:
    - fork(): https://pubs.opengroup.org/onlinepubs/9699919799/functions/fork.html
    - exec family: https://pubs.opengroup.org/onlinepubs/9699919799/functions/exec.html
    - waitpid(): https://pubs.opengroup.org/onlinepubs/9699919799/functions/wait.html
    - Exit status macros: https://pubs.opengroup.org/onlinepubs/9699919799/functions/wait.html
"""

import os
import sys
import signal
from typing import List, Dict, Any


def execute_external_command(args: List[str], config: Dict[str, Any]) -> int:
    """
    Execute external command using fork/exec/wait.

    This function demonstrates POSIX process management by:
    1. Forking the current process to create a child
    2. In child: replacing process image with command using execvp()
    3. In parent: waiting for child completion using waitpid()

    Args:
        args: Command arguments where args[0] is the command name.
              Must be non-empty list with at least one element.
        config: Configuration dictionary containing execution settings.

    Returns:
        Exit code from the executed command:
        - 0: Success
        - 1-125: Command-specific error codes
        - 126: Command not executable (permission denied)
        - 127: Command not found
        - 128+N: Terminated by signal N

    Raises:
        Does not raise exceptions - all errors are caught and returned as exit codes.

    Example:
        >>> config = {'execution': {'show_exit_codes': 'always'}}
        >>> execute_external_command(['ls', '-la'], config)
        [Exit: 0]
        0
        >>> execute_external_command(['nonexistent_cmd'], config)
        nonexistent_cmd: command not found
        [Exit: 127]
        127
    """
    # Input validation (defensive programming)
    if not args:
        print("Error: No command specified", file=sys.stderr)
        return 1

    # Debug output if enabled
    # Handle None values in config (malformed config)
    debug_config = config.get("debug", {})
    if debug_config is None:
        debug_config = {}
    if debug_config.get("show_fork_pids", False):
        print(f"[About to fork for: {args[0]}]", file=sys.stderr)

    # Step 1: Fork the process
    # POSIX fork() creates an exact duplicate of the current process.
    # Both parent and child continue from this point, but fork() returns:
    #   - 0 in the child process
    #   - child's PID in the parent process
    #   - -1 on error (raises OSError in Python)
    # Reference: https://pubs.opengroup.org/onlinepubs/9699919799/functions/fork.html
    try:
        pid = os.fork()
    except OSError as e:
        # Fork can fail if system resource limits are reached
        # Common errors: EAGAIN (process limit), ENOMEM (out of memory)
        print(f"Error: Fork failed: {e}", file=sys.stderr)
        return 1

    # Step 2: Handle child and parent differently
    if pid == 0:
        # CHILD PROCESS PATH
        # CRITICAL: Reset signal handlers to default so child can be interrupted
        # Without this, Ctrl+C would kill the parent shell
        # This MUST be the first thing done in the child process to avoid race conditions
        signal.signal(signal.SIGINT, signal.SIG_DFL)

        # Try to replace process image with the command
        # POSIX execvp() replaces the current process image with a new one.
        # It searches PATH for the executable and passes arguments as a vector.
        # On success, this call NEVER returns (process image is completely replaced).
        # Only returns (implicitly via exception) if exec fails.
        # Reference: https://pubs.opengroup.org/onlinepubs/9699919799/functions/exec.html
        try:
            os.execvp(args[0], args)
        except FileNotFoundError:
            # Command not found in PATH
            # Use POSIX standard exit code 127
            print(f"{args[0]}: command not found", file=sys.stderr)
            os._exit(
                127
            )  # CRITICAL: Must use os._exit(), NOT return! (bypasses Python cleanup)
        except PermissionError:
            # Command found but not executable
            # Use POSIX standard exit code 126
            print(f"{args[0]}: Permission denied", file=sys.stderr)
            os._exit(
                126
            )  # CRITICAL: Must use os._exit(), NOT return! (bypasses Python cleanup)
        except Exception as e:
            # Catch any other unexpected errors
            # Use generic error code 1
            print(f"{args[0]}: {e}", file=sys.stderr)
            os._exit(
                1
            )  # CRITICAL: Must use os._exit(), NOT return! (bypasses Python cleanup)

    else:
        # PARENT PROCESS PATH
        # Debug output showing child PID
        # Handle None values in config (malformed config)
        debug_config = config.get("debug", {})
        if debug_config is None:
            debug_config = {}
        if debug_config.get("show_fork_pids", False):
            print(f"[Forked child PID: {pid}]", file=sys.stderr)

        # Step 3: Wait for child to complete
        # POSIX waitpid() suspends execution until the specified child changes state.
        # With options=0, it waits for termination (not stop/continue).
        # Returns tuple: (child_pid, status)
        # status is encoded - use POSIX macros (WIFEXITED, WEXITSTATUS, etc.) to decode.
        # Reference: https://pubs.opengroup.org/onlinepubs/9699919799/functions/wait.html
        try:
            child_pid, status = os.waitpid(pid, 0)
        except ChildProcessError:
            # This shouldn't happen (child already reaped)
            # But handle it defensively
            print("Error: Child process not found", file=sys.stderr)
            return 1

        # Step 4: Display exit status if configured
        display_exit_status(status, config)

        # Step 5: Extract and return exit code using POSIX status macros
        # POSIX defines macros to interpret the encoded wait status:
        # - WIFEXITED(status): True if child exited normally via exit() or return
        # - WEXITSTATUS(status): Extract exit code (0-255) if WIFEXITED is true
        # - WIFSIGNALED(status): True if child was terminated by signal
        # - WTERMSIG(status): Extract signal number if WIFSIGNALED is true
        # Reference: https://pubs.opengroup.org/onlinepubs/9699919799/functions/wait.html
        if os.WIFEXITED(status):
            # Process exited normally - extract exit code (0-255)
            return os.WEXITSTATUS(status)
        elif os.WIFSIGNALED(status):
            # Process was terminated by signal (e.g., SIGKILL, SIGTERM, SIGSEGV)
            # Return 128 + signal number (POSIX convention for signal termination)
            return 128 + os.WTERMSIG(status)
        else:
            # Process was stopped or continued (shouldn't happen with default waitpid)
            # Return generic error code
            return 1


def display_exit_status(status: int, config: Dict[str, Any]) -> None:
    """
    Display exit status based on configuration.

    Shows exit code or signal termination information depending on
    the configuration setting for show_exit_codes.

    Args:
        status: Raw process exit status from os.waitpid()
        config: Configuration dictionary with execution settings

    Configuration:
        config['execution']['show_exit_codes']:
            - 'never': Never display exit codes
            - 'on_failure': Display only for non-zero exit codes
            - 'always': Always display exit codes
        config['execution']['exit_code_format']:
            - Format string for exit code display (default: '[Exit: {code}]')
            - Must contain {code} placeholder

    Returns:
        None - prints to stdout or stderr

    Example:
        >>> config = {'execution': {'show_exit_codes': 'always', 'exit_code_format': '[Exit: {code}]'}}
        >>> # Simulate status for exit code 0
        >>> display_exit_status(0, config)
        [Exit: 0]
        >>> # Simulate status for exit code 1
        >>> display_exit_status(256, config)  # 256 = 1 << 8
        [Exit: 1]
    """
    # Get configuration settings with defaults
    # Handle None values in config (malformed config)
    execution_config = config.get("execution", {})
    if execution_config is None:
        execution_config = {}
    show_mode = execution_config.get("show_exit_codes", "on_failure")
    format_str = execution_config.get("exit_code_format", "[Exit: {code}]")

    # Check how the process terminated
    if os.WIFEXITED(status):
        # Process exited normally
        exit_code = os.WEXITSTATUS(status)

        # Determine if we should display based on mode
        should_display = False
        if show_mode == "always":
            should_display = True
        elif show_mode == "on_failure" and exit_code != 0:
            should_display = True
        elif show_mode == "never":
            should_display = False

        # Display if configured
        if should_display:
            # Use format string from config
            # Guard against non-string format values (None, int, etc.)
            if not isinstance(format_str, str):
                format_str = "[Exit: {code}]"

            # Handle format errors gracefully
            try:
                message = format_str.format(code=exit_code)
                print(message)
            except (KeyError, ValueError, AttributeError):
                # Format string is invalid - use default
                print(f"[Exit: {exit_code}]")

    elif os.WIFSIGNALED(status):
        # Process was terminated by signal
        signal_num = os.WTERMSIG(status)
        # Always show signal termination (not configurable)
        # This is important information for user
        print(f"[Terminated by signal {signal_num}]", file=sys.stderr)

    elif os.WIFSTOPPED(status):
        # Process was stopped (shouldn't happen with default waitpid)
        # But handle it for completeness
        signal_num = os.WSTOPSIG(status)
        print(f"[Stopped by signal {signal_num}]", file=sys.stderr)

    # Note: WIFCONTINUED exists on some systems but not all
    # We don't handle it as it's rare and not relevant for our use case
