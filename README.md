# AkujobiP1Shell

![CI](https://github.com/jakujobi/AkujobiP1Shell/workflows/CI/badge.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![Tests](https://img.shields.io/badge/tests-229%20passing-success)
![Coverage](https://img.shields.io/badge/coverage-89%25-yellowgreen)

A POSIX-compliant command-line shell demonstrating process management using fork/exec/wait system calls.

**Author:** John Akujobi  
**Website:** jakujobi.com  
**Email:** john@jakujobi.com  
**Course:** CSC456 - Operating Systems  
**Version:** 1.0.0

## Features

- POSIX process management (fork/exec/wait pattern)
- Built-in commands: `exit`, `cd`, `pwd`, `help`
- Quote handling (single and double quotes)
- Wildcard expansion (`*`, `?`, `[...]`)
- Configurable behavior via YAML
- Signal handling (Ctrl+C, Ctrl+D)
- Exit code display and formatting
- Comprehensive error handling
- 229 passing tests with 89% coverage

---

## Requirements

- Python 3.10 or higher
- Linux (Ubuntu recommended)
- `python3-venv` package (for virtual environment)

---

## Quick Start

### Prerequisites

**IMPORTANT:** You need administrator privileges (sudo) to install `python3-venv`:

```bash
sudo apt install python3-venv
```

Or for Python 3.12 specifically:
```bash
sudo apt install python3.12-venv
```

### One-Command Setup

After installing `python3-venv` with sudo, simply run this **single command**:

```bash
./activate.sh
```

This script will:
- Check if you're in the correct project directory
- Check if `python3-venv` is installed (with clear error if not)
- Test that virtual environment creation works
- Create/verify the virtual environment (~50-100MB disk space)
- Install the package and dependencies
- Activate the virtual environment
- Set everything up automatically

**Note:** If you see an error about `python3-venv` not being installed, you must install it with `sudo` first (see Prerequisites above).

### After Setup

The virtual environment will be activated automatically. You can then run the shell:

```bash
akujobip1
```

Or:
```bash
python -m akujobip1
```

---

## Development

### Activating the Virtual Environment

Always activate the virtual environment before working on the project:

```bash
source venv/bin/activate
```

### Installing Dependencies

```bash
# Install runtime dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -e ".[dev]"
```

### Running Tests

```bash
# Run all tests
pytest -v

# Run with coverage
pytest --cov=akujobip1 --cov-report=html

# Run bash integration tests
./tests/run_tests.sh

# Run specific test file
pytest tests/test_executor.py -v

# Run linter
ruff check src/

# Check formatting
black --check src/
```

### Development Workflow

1. **Activate virtual environment**: `source venv/bin/activate`
2. **Make changes**: Edit source files in `src/akujobip1/`
3. **Run tests**: `pytest` to verify no breakage
4. **Check lint**: `ruff check src/` for code quality
5. **Check format**: `black --check src/` for style
6. **Format code**: `black src/` to auto-format
7. **Run shell**: `akujobip1` to test interactively

---

## Project Structure

```
AkujobiP1Shell/
├── src/
│   └── akujobip1/
│       ├── __init__.py
│       ├── shell.py      # Main REPL loop
│       ├── config.py     # Configuration management
│       ├── parser.py     # Command parsing
│       ├── builtins.py   # Built-in commands
│       └── executor.py   # Process execution
├── examples/
│   └── config.yaml       # Example configuration
├── tests/                # Test files
├── docs/                 # Documentation
├── akujobip1.yaml        # Default configuration
├── pyproject.toml        # Package configuration
└── requirements.txt      # Python dependencies
```

---

## Usage Examples

### Basic Commands

```bash
$ akujobip1
AkujobiP1> pwd
/home/user/dev/AkujobiP1Shell

AkujobiP1> ls -la
total 48
drwxr-xr-x 8 user user 4096 Nov 10 10:00 .
drwxr-xr-x 3 user user 4096 Nov 10 09:00 ..

AkujobiP1> echo "Hello, World!"
Hello, World!

AkujobiP1> cd /tmp

AkujobiP1> exit
Bye!
```

### Built-in Commands

```bash
AkujobiP1> help
Built-in commands:
  exit       Exit the shell
  cd [dir]   Change directory (cd - for previous, cd for home)
  pwd        Print working directory
  help       Show this help message

AkujobiP1> cd              # Go to home directory
AkujobiP1> cd /tmp         # Go to /tmp
AkujobiP1> cd -            # Go back to previous directory
```

### Wildcards

```bash
AkujobiP1> ls *.py
file1.py  file2.py  test.py

AkujobiP1> echo test*
test.py test_helpers.py
```

### Quoted Arguments

```bash
AkujobiP1> echo "hello world"
hello world

AkujobiP1> printf "%s %s\n" "first arg" "second arg"
first arg second arg
```

---

## Configuration

The shell can be configured using YAML files. Configuration is loaded in priority order (highest to lowest):

1. `$AKUJOBIP1_CONFIG` environment variable (path to config file)
2. `./akujobip1.yaml` (current directory)
3. `~/.config/akujobip1/config.yaml` (user config)
4. Built-in defaults

### Complete Configuration Reference

```yaml
# Prompt configuration
prompt:
  text: "AkujobiP1> "                    # Prompt string

# Exit command configuration
exit:
  message: "Bye!"                        # Message shown when exiting

# External command execution
execution:
  show_exit_codes: "on_failure"         # Options: never, on_failure, always
  exit_code_format: "[Exit: {code}]"    # Format string ({code} placeholder)

# Wildcard expansion
glob:
  enabled: true                          # Enable wildcard expansion
  show_expansions: false                 # Show expanded arguments

# Built-in commands
builtins:
  cd:
    enabled: true                        # Enable cd command
    show_pwd_after: false                # Show pwd after cd
  pwd:
    enabled: true                        # Enable pwd command
  help:
    enabled: true                        # Enable help command

# Error handling
errors:
  verbose: false                         # Show full Python tracebacks

# Debug settings
debug:
  log_commands: false                    # Log commands to file
  log_file: "~/.akujobip1.log"          # Log file path
  show_fork_pids: false                  # Show child PIDs
```

### Configuration Examples

**Minimal config** (`~/.config/akujobip1/config.yaml`):
```yaml
prompt:
  text: "$ "
exit:
  message: "Goodbye!"
```

**Verbose config** (for debugging):
```yaml
execution:
  show_exit_codes: "always"
errors:
  verbose: true
debug:
  show_fork_pids: true
  log_commands: true
```

**Custom config via environment**:
```bash
export AKUJOBIP1_CONFIG="/path/to/custom/config.yaml"
akujobip1
```

---

## Architecture

The shell is organized into five main modules:

- **shell.py** (205 lines) - Main REPL loop, signal handling, error recovery
- **config.py** (272 lines) - YAML configuration loading and merging
- **parser.py** (141 lines) - Command parsing, quote handling, wildcards
- **builtins.py** (244 lines) - Built-in commands (exit, cd, pwd, help)
- **executor.py** (229 lines) - Fork/exec/wait implementation

### Process Execution Flow

1. User enters command at prompt
2. Command is parsed (tokenization, quote removal, wildcard expansion)
3. Check if command is built-in:
   - **Yes**: Execute directly in shell process
   - **No**: Fork child process, exec command, wait for completion
4. Display exit code if configured
5. Return to prompt

### POSIX System Calls Used

- `fork()` - Create child process
- `execvp()` - Replace process image with command
- `waitpid()` - Wait for child to complete
- `chdir()` - Change directory (cd command)
- `getcwd()` - Get current directory (pwd command)

For detailed documentation, see `docs/report.md` and `docs/diagrams/`.

---

## Troubleshooting

### "externally-managed-environment" Error

If you see this error when running `pip install -e .`, you need to use a virtual environment. Use the setup script:

```bash
./activate.sh
```

### "python3-venv not found" or "ensurepip is not available"

**You need sudo (administrator privileges) to install python3-venv:**

```bash
sudo apt install python3-venv
```

Or for Python 3.12:
```bash
sudo apt install python3.12-venv
```

After installing, run `./activate.sh` again.

### Command Not Found After Install

If `akujobip1` command is not found:

```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Verify installation
pip show AkujobiP1

# Reinstall if needed
pip install -e .
```

### Shell Won't Start

```bash
# Check Python version (need 3.10+)
python3 --version

# Try running directly
python -m akujobip1

# Check for errors in config
python3 -c "import yaml; yaml.safe_load(open('akujobip1.yaml'))"
```

### Tests Failing

```bash
# Make sure you're in virtual environment
source venv/bin/activate

# Reinstall dependencies
pip install -e ".[dev]"

# Run tests with verbose output
pytest -v

# Check specific test
pytest tests/test_executor.py::test_function_name -v
```

---

## Documentation

- **Main Report** (`docs/report.md`) - Comprehensive 20+ page documentation
- **Architecture Diagrams** (`docs/diagrams/`) - Visual documentation (Mermaid)
  - Component architecture
  - Data flow
  - System call sequence
  - Configuration loading
- **Code Documentation** - All modules have comprehensive docstrings
- **Examples** (`examples/`) - Configuration examples and usage guides

## Contributing

This is an academic project for CSC456. For questions or issues:

- Email: john@jakujobi.com
- Website: jakujobi.com

---

## License

This project is part of CSC456 Programming Assignment 1.

## Acknowledgments

- POSIX standards documentation
- Python documentation (os, shlex, glob modules)
- CSC456 course materials and lectures

---

**Version:** 1.0.0  
**Last Updated:** November 2025
