"""
Main shell module - REPL loop and entry point.

This module contains the main command-line interface and REPL loop
for the AkujobiP1Shell. It integrates all other modules (config, parser,
builtins, executor) to provide a complete shell experience.

Signal Handling Strategy:
    We do NOT use custom signal handlers. Python's default SIGINT behavior
    works perfectly:
    - During input(): Raises KeyboardInterrupt -> we catch it
    - During command execution: Signal goes to child process -> executor handles it
    
    This approach is simpler and safer than custom handlers, which could
    interfere with waitpid() and child process signal handling.
"""

import sys
from typing import Dict, Any

# Import all required modules
from akujobip1.config import load_config
from akujobip1.parser import parse_command
from akujobip1.builtins import get_builtin
from akujobip1.executor import execute_external_command


def cli() -> int:
    """
    Main entry point for the shell application.
    
    This function is called when the shell is started either via
    the command line (akujobip1) or as a module (python -m akujobip1).
    
    Returns:
        Exit code (0 for success, non-zero for error)
    
    Environment Variables:
        AKUJOBIP1_CONFIG: Path to custom configuration file
    
    Example:
        $ akujobip1
        AkujobiP1> ls
        file1.txt  file2.txt
        AkujobiP1> exit
        Bye!
    
    Error Handling:
        - Catches KeyboardInterrupt during startup (Ctrl+C) -> exits gracefully
        - Catches unexpected exceptions during startup -> prints error, exits with code 1
    """
    try:
        # Load configuration from YAML file or use defaults
        config = load_config()
        
        # Run main shell loop
        return run_shell(config)
        
    except KeyboardInterrupt:
        # Ctrl+C during startup - exit gracefully
        print()
        return 0
    
    except Exception as e:
        # Fatal error during startup
        print(f"Fatal error: {e}", file=sys.stderr)
        return 1


def run_shell(config: Dict[str, Any]) -> int:
    """
    Run the main REPL (Read-Eval-Print Loop).
    
    Main loop structure:
    1. Display prompt and read input
    2. Parse command (handles quotes, wildcards)
    3. Skip if empty
    4. Check if built-in command
    5. Execute built-in or external command
    6. Check for exit signal (-1 from exit command)
    7. Repeat
    
    Args:
        config: Configuration dictionary containing all shell settings
    
    Returns:
        Exit code (0 for normal exit, non-zero for error)
    
    Signal Handling:
        - EOFError (Ctrl+D): Exits shell gracefully with exit message
        - KeyboardInterrupt (Ctrl+C): Cancels current line, shows new prompt
        - Unexpected exceptions: Prints error and continues (defensive)
    
    Example:
        >>> config = {'prompt': {'text': 'shell> '}, 'exit': {'message': 'Goodbye!'}}
        >>> run_shell(config)  # Runs until user types 'exit' or presses Ctrl+D
        shell> ls
        file1.txt
        shell> exit
        Goodbye!
        0
    
    Critical Implementation Notes:
        - Exit command returns -1 (not 0) to signal shell termination
        - Parser returns [] for empty/invalid input - must check before indexing
        - Config keys accessed with .get() to handle missing keys gracefully
        - NO custom signal handlers - Python's default behavior is correct
    """
    # Extract configuration values with safe defaults
    # Use .get() with nested dicts to handle missing keys gracefully
    # Handle case where config values might be None
    prompt_config = config.get('prompt', {})
    if prompt_config is None:
        prompt_config = {}
    prompt = prompt_config.get('text', 'AkujobiP1> ')
    
    exit_config = config.get('exit', {})
    if exit_config is None:
        exit_config = {}
    exit_message = exit_config.get('message', 'Bye!')
    
    # Main REPL loop - continues until exit command or Ctrl+D
    while True:
        try:
            # Step 1: Display prompt and read input
            # input() automatically flushes stdout and handles line buffering
            command_line = input(prompt)
            
            # Step 2: Parse command line into arguments
            # Parser handles quotes, escapes, wildcards, and errors
            # Returns empty list for empty/whitespace/invalid input
            args = parse_command(command_line, config)
            
            # Step 3: Skip empty commands (empty input, whitespace, parse errors)
            # Parser already printed error message if parsing failed
            if not args:
                continue
            
            # Step 4: Check if command is a built-in
            # Built-ins are executed directly without forking
            builtin = get_builtin(args[0])
            
            if builtin:
                # Step 5a: Execute built-in command
                exit_code = builtin.execute(args, config)
                
                # Step 6: Check for exit signal
                # Exit command returns -1 to signal shell termination
                # This is the ONLY way to exit the shell normally
                if exit_code == -1:
                    # Exit command executed successfully
                    # Note: exit command already printed exit message
                    return 0
                
                # Non-exit built-ins return 0 for success, 1+ for error
                # We don't display their exit codes (they handle their own output)
            else:
                # Step 5b: Execute external command
                # Executor handles fork/exec/wait and displays exit codes if configured
                exit_code = execute_external_command(args, config)
            
            # Step 7: Continue loop
            # Exit codes are displayed by executor if configured
            # (show_exit_codes: never/on_failure/always)
            
        except EOFError:
            # Ctrl+D pressed - exit gracefully like exit command
            print()  # Newline after ^D (cursor is at end of line)
            print(exit_message)
            return 0
            
        except KeyboardInterrupt:
            # Ctrl+C pressed during input - cancel current line, show new prompt
            # This does NOT exit the shell (unlike Ctrl+D)
            print()  # Newline after ^C (cursor is at end of line)
            continue  # Show new prompt
        
        except Exception as e:
            # Unexpected error - defensive programming
            # Shell should be resilient and not crash on unexpected errors
            print(f"Shell error: {e}", file=sys.stderr)
            
            # If verbose error mode is enabled, show traceback
            if config.get('errors', {}).get('verbose', False):
                import traceback
                traceback.print_exc()
            
            # Continue shell - user can still type commands or exit
            continue
    
    # Should never reach here (loop exits via return statements)
    # But if we do, return success code
    return 0

