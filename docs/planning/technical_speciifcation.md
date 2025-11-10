# AkujobiP1Shell - Technical Specification

**Project:** CSC456 Programming Assignment 1
**Author:** John Akujobi
**Date:** 2025-11-09
**Version:** 1.0

---

## Table of Contents

1. [System Architecture](#1-system-architecture)
2. [Module Specifications](#2-module-specifications)
3. [API Documentation](#3-api-documentation)
4. [Data Structures](#4-data-structures)
5. [Process Flow](#5-process-flow)
6. [Error Handling Strategy](#6-error-handling-strategy)
7. [Configuration Schema](#7-configuration-schema)
8. [Testing Strategy](#8-testing-strategy)

---

## 1. System Architecture

### 1.1 Component Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      AkujobiP1 Shell                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐      ┌──────────────┐                   │
│  │   Main Loop  │◄────►│    Config    │                   │
│  │  (shell.py)  │      │  (config.py) │                   │
│  └──────┬───────┘      └──────────────┘                   │
│         │                                                   │
│         │                                                   │
│         ▼                                                   │
│  ┌──────────────┐      ┌──────────────┐                   │
│  │    Parser    │      │   Builtins   │                   │
│  │ (parser.py)  │      │(builtins.py) │                   │
│  └──────┬───────┘      └──────┬───────┘                   │
│         │                     │                            │
│         │                     │                            │
│         ▼                     ▼                            │
│  ┌──────────────────────────────────┐                     │
│  │         Executor                 │                     │
│  │       (executor.py)              │                     │
│  │  ┌────────────┐  ┌────────────┐ │                     │
│  │  │  fork()    │  │  execvp()  │ │                     │
│  │  │  wait()    │  │  error     │ │                     │
│  │  └────────────┘  └────────────┘ │                     │
│  └──────────────────────────────────┘                     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 Data Flow

```
User Input
   │
   ▼
┌──────────────────┐
│  Read Input      │  (input() in main loop)
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  Parse Command   │  (shlex.split, wildcard expansion)
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  Check Type      │  (Built-in or External?)
└────┬────────┬────┘
     │        │
     │        └──────────────┐
     │                       │
     ▼                       ▼
┌──────────────┐    ┌──────────────────┐
│   Execute    │    │   Execute        │
│   Built-in   │    │   External       │
│              │    │   (fork/exec)    │
└──────┬───────┘    └────────┬─────────┘
       │                     │
       └──────────┬──────────┘
                  │
                  ▼
         ┌──────────────────┐
         │  Display Result  │
         └────────┬─────────┘
                  │
                  ▼
         ┌──────────────────┐
         │  Show Prompt     │
         └──────────────────┘
```

---

## 2. Module Specifications

### 2.1 shell.py (Main Shell Module)

**Purpose:** Main entry point and REPL loop

**Dependencies:**

- `os`, `sys`, `signal`
- Internal: `config`, `parser`, `builtins`, `executor`

**Key Functions:**

```python
def cli() -> int:
    """
    Main entry point for the shell application.

    Returns:
        Exit code (0 for success)
    """

def run_shell(config: dict) -> int:
    """
    Run the main REPL loop.

    Args:
        config: Configuration dictionary

    Returns:
        Exit code
    """

def setup_signal_handlers() -> None:
    """
    Set up signal handlers for SIGINT (Ctrl+C).
    """

def sigint_handler(signum: int, frame) -> None:
    """
    Handle SIGINT (Ctrl+C) by showing new prompt.
    """
```

**Pseudocode:**

```python
def cli():
    # Load configuration
    config = load_config()

    # Set up signal handlers
    setup_signal_handlers()

    # Run shell
    return run_shell(config)

def run_shell(config):
    prompt = config['prompt']['text']

    while True:
        try:
            # Display prompt and read input
            command_line = input(prompt)

            # Parse command
            args = parse_command(command_line, config)

            # Skip empty commands
            if not args:
                continue

            # Check if built-in
            builtin = get_builtin(args[0])
            if builtin:
                exit_code = builtin.execute(args, config)
                if args[0] == 'exit':
                    return exit_code
            else:
                # Execute external command
                execute_external_command(args, config)

        except EOFError:
            # Ctrl+D pressed
            print()
            print(config['exit']['message'])
            return 0
        except KeyboardInterrupt:
            # Ctrl+C pressed (shouldn't normally reach here)
            print()
            continue
```

---

### 2.2 config.py (Configuration Management)

**Purpose:** Load and manage configuration from YAML files

**Dependencies:**

- `yaml` (PyYAML)
- `os`, `pathlib`

**Key Functions:**

```python
def load_config() -> dict:
    """
    Load configuration from files with priority order:
    1. $AKUJOBIP1_CONFIG environment variable
    2. ./akujobip1.yaml (current directory)
    3. ~/.config/akujobip1/config.yaml
    4. Built-in defaults

    Returns:
        Configuration dictionary
    """

def merge_config(base: dict, override: dict) -> dict:
    """
    Deep merge two configuration dictionaries.

    Args:
        base: Base configuration (defaults)
        override: Override configuration (user settings)

    Returns:
        Merged configuration
    """

def validate_config(config: dict) -> bool:
    """
    Validate configuration structure and values.

    Args:
        config: Configuration to validate

    Returns:
        True if valid, False otherwise
    """

def get_default_config() -> dict:
    """
    Get default configuration values.

    Returns:
        Default configuration dictionary
    """
```

**Default Configuration:**

```python
DEFAULT_CONFIG = {
    'prompt': {
        'text': 'AkujobiP1> '
    },
    'exit': {
        'message': 'Bye!'
    },
    'execution': {
        'show_exit_codes': 'on_failure',  # never, on_failure, always
        'exit_code_format': '[Exit: {code}]'
    },
    'glob': {
        'enabled': True,
        'show_expansions': False
    },
    'builtins': {
        'cd': {
            'enabled': True,
            'show_pwd_after': False
        },
        'pwd': {
            'enabled': True
        },
        'help': {
            'enabled': True
        }
    },
    'errors': {
        'verbose': False
    },
    'debug': {
        'log_commands': False,
        'log_file': '~/.akujobip1.log',
        'show_fork_pids': False
    }
}
```

---

### 2.3 parser.py (Command Parser)

**Purpose:** Parse command line input into executable arguments

**Dependencies:**

- `shlex`
- `glob`

**Key Functions:**

```python
def parse_command(command_line: str, config: dict) -> list[str]:
    """
    Parse command line into list of arguments.

    Handles:
    - Quoted arguments (single and double quotes)
    - Wildcard expansion (*, ?, [...])
    - Empty input
    - Whitespace normalization

    Args:
        command_line: Raw command line string
        config: Configuration dictionary

    Returns:
        List of arguments (empty list for empty input)

    Example:
        >>> parse_command('ls -la', config)
        ['ls', '-la']
        >>> parse_command('echo "hello world"', config)
        ['echo', 'hello world']
        >>> parse_command('ls *.txt', config)
        ['ls', 'file1.txt', 'file2.txt']
    """

def expand_wildcards(args: list[str]) -> list[str]:
    """
    Expand wildcard patterns in arguments.

    Args:
        args: List of arguments (may contain wildcards)

    Returns:
        List with wildcards expanded to matching files

    Example:
        >>> expand_wildcards(['ls', '*.txt'])
        ['ls', 'file1.txt', 'file2.txt']
        >>> expand_wildcards(['echo', 'no*match'])
        ['echo', 'no*match']  # No matches, return literal
    """
```

**Implementation Details:**

```python
import shlex
import glob as glob_module

def parse_command(command_line, config):
    # Strip whitespace
    command_line = command_line.strip()

    # Handle empty input
    if not command_line:
        return []

    # Use shlex for proper quote handling
    try:
        args = shlex.split(command_line)
    except ValueError as e:
        # Invalid quoting (e.g., unclosed quote)
        print(f"Syntax error: {e}", file=sys.stderr)
        return []

    # Expand wildcards if enabled
    if config['glob']['enabled']:
        args = expand_wildcards(args)
        if config['glob']['show_expansions']:
            print(f"Expanded to: {args}")

    return args

def expand_wildcards(args):
    expanded = []
    for arg in args:
        # Check if argument contains wildcard characters
        if any(char in arg for char in ['*', '?', '[']):
            matches = glob_module.glob(arg)
            if matches:
                # Sort for consistent output
                expanded.extend(sorted(matches))
            else:
                # No matches, keep literal
                expanded.append(arg)
        else:
            expanded.append(arg)
    return expanded
```

---

### 2.4 builtins.py (Built-in Commands)

**Purpose:** Implement shell built-in commands

**Dependencies:**

- `os`, `sys`

**Class Hierarchy:**

```python
class BuiltinCommand:
    """Base class for built-in commands."""

    def execute(self, args: list[str], config: dict) -> int:
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

    def execute(self, args, config):
        print(config['exit']['message'])
        return 0

class CdCommand(BuiltinCommand):
    """Change directory."""

    def execute(self, args, config):
        if len(args) == 1:
            # No argument, go to home
            target = os.path.expanduser('~')
        else:
            target = args[1]

        try:
            os.chdir(target)
            if config['builtins']['cd']['show_pwd_after']:
                print(os.getcwd())
            return 0
        except FileNotFoundError:
            print(f"cd: {target}: No such file or directory", file=sys.stderr)
            return 1
        except NotADirectoryError:
            print(f"cd: {target}: Not a directory", file=sys.stderr)
            return 1
        except PermissionError:
            print(f"cd: {target}: Permission denied", file=sys.stderr)
            return 1

class PwdCommand(BuiltinCommand):
    """Print working directory."""

    def execute(self, args, config):
        print(os.getcwd())
        return 0

class HelpCommand(BuiltinCommand):
    """Show help information."""

    def execute(self, args, config):
        print("Built-in commands:")
        print("  exit - Exit the shell")
        print("  cd [dir] - Change directory")
        print("  pwd - Print working directory")
        print("  help - Show this help message")
        return 0
```

**Registry:**

```python
BUILTINS = {
    'exit': ExitCommand(),
    'cd': CdCommand(),
    'pwd': PwdCommand(),
    'help': HelpCommand()
}

def get_builtin(name: str) -> BuiltinCommand | None:
    """
    Get built-in command by name.

    Args:
        name: Command name

    Returns:
        BuiltinCommand instance or None if not found
    """
    return BUILTINS.get(name)
```

---

### 2.5 executor.py (External Command Executor)

**Purpose:** Execute external commands using fork/exec/wait

**Dependencies:**

- `os`, `sys`, `signal`

**Key Functions:**

```python
def execute_external_command(args: list[str], config: dict) -> int:
    """
    Execute external command using fork/exec/wait.

    Process:
    1. Fork process
    2. Child: exec command
    3. Parent: wait for child
    4. Return exit status

    Args:
        args: Command arguments (args[0] is command name)
        config: Configuration dictionary

    Returns:
        Exit code of command
    """

def display_exit_status(status: int, config: dict) -> None:
    """
    Display exit status if configured.

    Args:
        status: Process exit status from waitpid
        config: Configuration dictionary
    """
```

**Implementation:**

```python
import os
import sys
import signal

def execute_external_command(args, config):
    """
    Execute external command using POSIX fork/exec/wait.
    """
    try:
        # Create child process using fork() system call
        # Returns 0 in child, child PID in parent
        pid = os.fork()
    except OSError as e:
        # Fork can fail due to resource limits
        print(f"Error: Failed to fork process: {e}", file=sys.stderr)
        return 1

    if pid == 0:
        # Child process execution path

        # Reset signal handlers to default
        # This allows child to be interrupted by Ctrl+C
        signal.signal(signal.SIGINT, signal.SIG_DFL)

        try:
            # Replace child process image with command
            # execvp() searches PATH and never returns on success
            os.execvp(args[0], args)
        except FileNotFoundError:
            # Command not found in PATH
            # Exit with POSIX standard code 127
            print(f"{args[0]}: command not found", file=sys.stderr)
            sys.exit(127)
        except PermissionError:
            # Command exists but not executable
            # Exit with POSIX standard code 126
            print(f"{args[0]}: Permission denied", file=sys.stderr)
            sys.exit(126)
        except Exception as e:
            # Other errors
            print(f"{args[0]}: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        # Parent process execution path

        # Optionally display child PID for debugging
        if config['debug']['show_fork_pids']:
            print(f"[Forked child PID: {pid}]")

        try:
            # Wait for specific child process
            # Returns (child_pid, status) tuple
            child_pid, status = os.waitpid(pid, 0)
        except ChildProcessError:
            # Child already reaped (shouldn't happen)
            return 1

        # Display exit status if configured
        display_exit_status(status, config)

        # Extract and return exit code
        if os.WIFEXITED(status):
            return os.WEXITSTATUS(status)
        elif os.WIFSIGNALED(status):
            # Process terminated by signal
            # Return 128 + signal number (common convention)
            return 128 + os.WTERMSIG(status)
        else:
            return 1

def display_exit_status(status, config):
    """
    Display exit status based on configuration.
    """
    # Only display if process exited normally
    if not os.WIFEXITED(status):
        # Process was signaled
        if os.WIFSIGNALED(status):
            signal_num = os.WTERMSIG(status)
            print(f"[Terminated by signal {signal_num}]", file=sys.stderr)
        return

    exit_code = os.WEXITSTATUS(status)
    show_mode = config['execution']['show_exit_codes']

    # Determine if we should display
    should_display = False
    if show_mode == 'always':
        should_display = True
    elif show_mode == 'on_failure' and exit_code != 0:
        should_display = True
    elif show_mode == 'never':
        should_display = False

    # Display if configured
    if should_display:
        fmt = config['execution']['exit_code_format']
        print(fmt.format(code=exit_code))
```

---

## 3. API Documentation

### 3.1 Public API

**Entry Point:**

```python
def cli() -> int:
    """
    Main entry point for AkujobiP1 shell.

    This function is called when the shell is started either via
    the command line (`akujobip1`) or as a module (`python -m akujobip1`).

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
    """
```

### 3.2 Internal API

**Configuration:**

```python
def load_config() -> dict
def merge_config(base: dict, override: dict) -> dict
def validate_config(config: dict) -> bool
```

**Parsing:**

```python
def parse_command(command_line: str, config: dict) -> list[str]
def expand_wildcards(args: list[str]) -> list[str]
```

**Built-ins:**

```python
def get_builtin(name: str) -> BuiltinCommand | None
class BuiltinCommand:
    def execute(args: list[str], config: dict) -> int
```

**Execution:**

```python
def execute_external_command(args: list[str], config: dict) -> int
def display_exit_status(status: int, config: dict) -> None
```

---

## 4. Data Structures

### 4.1 Configuration Dictionary

```python
config = {
    'prompt': {
        'text': str  # Prompt string
    },
    'exit': {
        'message': str  # Exit message
    },
    'execution': {
        'show_exit_codes': str,  # "never" | "on_failure" | "always"
        'exit_code_format': str  # Format string with {code} placeholder
    },
    'glob': {
        'enabled': bool,           # Enable wildcard expansion
        'show_expansions': bool    # Show expanded arguments
    },
    'builtins': {
        '<command>': {
            'enabled': bool,
            # Command-specific options
        }
    },
    'errors': {
        'verbose': bool
    },
    'debug': {
        'log_commands': bool,
        'log_file': str,
        'show_fork_pids': bool
    }
}
```

### 4.2 Command Arguments

```python
args = [
    str,  # args[0] = command name
    str,  # args[1] = first argument
    str,  # args[2] = second argument
    ...
]

# Example:
['ls', '-la', '/tmp']
['cp', 'file1.txt', 'file2.txt']
['echo', 'hello world']  # After quote parsing
```

---

## 5. Process Flow

### 5.1 Shell Startup

```
1. Entry point: cli()
   ↓
2. Load configuration
   ├→ Check $AKUJOBIP1_CONFIG
   ├→ Check ./akujobip1.yaml
   ├→ Check ~/.config/akujobip1/config.yaml
   └→ Use defaults
   ↓
3. Setup signal handlers
   └→ SIGINT → sigint_handler
   ↓
4. Enter main loop (run_shell)
```

### 5.2 Command Execution Flow

```
1. Display prompt
   ↓
2. Read input (input())
   ├→ EOFError → Print exit message, exit shell
   └→ KeyboardInterrupt → Show new prompt
   ↓
3. Parse command (parse_command)
   ├→ shlex.split() for tokenization
   └→ expand_wildcards() if enabled
   ↓
4. Check if empty
   ├→ Yes → Go to step 1
   └→ No → Continue
   ↓
5. Check if built-in (get_builtin)
   ├→ Yes → Execute built-in
   │   ├→ exit → Return from shell
   │   └→ Other → Go to step 1
   └→ No → Continue
   ↓
6. Execute external (execute_external_command)
   ├→ fork()
   │   ├→ Child → execvp()
   │   └→ Parent → waitpid()
   ↓
7. Display exit status if configured
   ↓
8. Go to step 1
```

### 5.3 Fork/Exec/Wait Process

```
Parent Process                  Child Process
──────────────                  ─────────────

fork()
  │
  ├──────────────────────────►  fork() returns 0
  │                              │
  │                              Reset signal handlers
  │                              │
  │                              execvp(command, args)
  │                              │
  │                              [Process image replaced]
  │                              │
  │                              [Command executes]
  │                              │
waitpid(pid)                     exit(status)
  │                              │
  │  ◄───────────────────────────┘
  │
Extract status
  │
Display exit code
  │
Return to main loop
```

---

## 6. Error Handling Strategy

### 6.1 Error Categories

| Category             | Handling Strategy           | Exit Behavior            |
| -------------------- | --------------------------- | ------------------------ |
| Configuration errors | Warn and use defaults       | Continue                 |
| Parse errors         | Display error message       | Continue to next command |
| Built-in errors      | Display error, return code  | Continue to next command |
| Command not found    | Display "command not found" | Continue to next command |
| Permission denied    | Display "Permission denied" | Continue to next command |
| Fork failure         | Display error               | Continue to next command |
| Signal (Ctrl+C)      | Cancel current line/command | Continue to next command |
| EOF (Ctrl+D)         | Print exit message          | Exit shell               |

### 6.2 Exit Codes

**POSIX Standard Exit Codes:**

- `0`: Success
- `1-125`: Command-specific errors
- `126`: Command found but not executable
- `127`: Command not found
- `128+N`: Terminated by signal N

**Shell Exit Codes:**

- `0`: Normal exit (via `exit` command or Ctrl+D)
- `1`: General error

### 6.3 Error Messages

**Format:**

```
{command}: {error_description}
```

**Examples:**

```
ls: cannot access 'nonexistent': No such file or directory
cd: /invalid: No such file or directory
notacommand: command not found
./nopermission.sh: Permission denied
```

---

## 7. Configuration Schema

### 7.1 YAML Schema

```yaml
# Type annotations for configuration file

prompt:
  text: string               # Required, default: "AkujobiP1> "

exit:
  message: string            # Required, default: "Bye!"

execution:
  show_exit_codes: enum      # never | on_failure | always
  exit_code_format: string   # Format with {code} placeholder

glob:
  enabled: boolean
  show_expansions: boolean

builtins:
  cd:
    enabled: boolean
    show_pwd_after: boolean
  pwd:
    enabled: boolean
  help:
    enabled: boolean

errors:
  verbose: boolean

debug:
  log_commands: boolean
  log_file: string           # Path (tilde expansion supported)
  show_fork_pids: boolean
```

### 7.2 Validation Rules

1. **Required fields:**

   - `prompt.text` (string, non-empty)
   - `exit.message` (string)
2. **Enum validation:**

   - `execution.show_exit_codes` must be one of: "never", "on_failure", "always"
3. **Type validation:**

   - All boolean fields must be true/false
   - All string fields must be strings
   - Nested dictionaries must match schema
4. **Path expansion:**

   - `~` in paths expanded to user home directory
   - Relative paths resolved from shell working directory

---

## 8. Testing Strategy

### 8.1 Unit Test Coverage

**Modules to Test:**

1. **config.py**

   - Test config loading from all locations
   - Test merging logic
   - Test validation
   - Test invalid YAML handling
   - Test missing files (default fallback)
2. **parser.py**

   - Test simple commands
   - Test quoted arguments (single/double quotes)
   - Test wildcards (match, no match, multiple)
   - Test empty input
   - Test invalid syntax
3. **builtins.py**

   - Test each built-in command
   - Test error cases (invalid args)
   - Test edge cases (cd with no args, etc.)
4. **executor.py**

   - Mock fork/exec/wait for testing
   - Test successful execution
   - Test command not found
   - Test permission errors
   - Test exit status handling
5. **shell.py**

   - Test main loop initialization
   - Test signal handling
   - Test EOF handling
   - Integration tests

### 8.2 Test Fixtures

```python
@pytest.fixture
def default_config():
    return get_default_config()

@pytest.fixture
def temp_config_file(tmp_path):
    config_file = tmp_path / "config.yaml"
    config_file.write_text("""
prompt:
  text: "Test> "
    """)
    return config_file

@pytest.fixture
def mock_fork():
    with patch('os.fork') as mock:
        mock.return_value = 1234
        yield mock
```

### 8.3 Test Examples

```python
def test_parse_simple_command():
    config = get_default_config()
    args = parse_command("ls -la", config)
    assert args == ['ls', '-la']

def test_parse_quoted_arguments():
    config = get_default_config()
    args = parse_command('echo "hello world"', config)
    assert args == ['echo', 'hello world']

def test_wildcard_expansion():
    # Create test files
    Path('test1.txt').touch()
    Path('test2.txt').touch()

    args = expand_wildcards(['ls', '*.txt'])
    assert 'test1.txt' in args
    assert 'test2.txt' in args

def test_cd_command():
    cmd = CdCommand()
    config = get_default_config()

    # Test cd to temp directory
    exit_code = cmd.execute(['cd', '/tmp'], config)
    assert exit_code == 0
    assert os.getcwd() == '/tmp'
```

---

## 9. Implementation Notes

### 9.1 Python Version Requirements

**Minimum:** Python 3.10

**Reason:** Type hints with `|` syntax (e.g., `str | None`)

**Alternative:** Use `typing.Union` for Python 3.9 compatibility

### 9.2 Dependencies

**Runtime:** None (uses only stdlib)

- `os`, `sys`, `signal`, `shlex`, `glob`, `pathlib`

**Development:**

- `pytest` >= 7.0 (testing)
- `pytest-cov` (coverage)
- `ruff` >= 0.5 (linting)
- `black` >= 24 (formatting)
- `PyYAML` (YAML parsing)

### 9.3 Platform-Specific Considerations

**Linux (Primary Target):**

- Full functionality
- All POSIX calls available

**Windows (Secondary):**

- `os.fork()` not available
- Fallback to `subprocess.Popen()`
- Limited functionality (no true process management demo)

**macOS:**

- Should work like Linux (POSIX-compliant)
- Not officially tested

### 9.4 Performance Considerations

**Fork/Exec Overhead:**

- Each external command creates new process
- Acceptable for interactive shell
- Not optimized for scripting many commands

**Configuration Loading:**

- Loaded once at startup
- Cached in memory
- No performance impact during execution

---

## 10. Security Considerations

### 10.1 Command Injection

**Not Vulnerable:**

- Uses `execvp()` with argument array
- No shell interpretation of arguments
- Wildcards expanded by shell (controlled)

**Example Safe:**

```python
args = ['ls', '; rm -rf /']  # Second arg is literal, not executed
```

### 10.2 Path Traversal

**Built-in cd command:**

- Uses standard `os.chdir()`
- Respects file system permissions
- No path sanitization needed (OS handles it)

### 10.3 Resource Limits

**Fork bomb protection:**

- None implemented (relies on OS limits)
- Consider adding max child limit in future

---

**Document Version:** 1.0
**Last Updated:** 2025-11-09
**Status:** Ready for Implementation