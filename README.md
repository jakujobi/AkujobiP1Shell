# AkujobiP1Shell

![CI](https://github.com/jakujobi/AkujobiP1Shell/workflows/CI/badge.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![Tests](https://img.shields.io/badge/tests-229%20passing-success)
![Coverage](https://img.shields.io/badge/coverage-89%25-yellowgreen)

A simple shell implementation using POSIX system calls for CSC456 Programming Assignment 1.

**Author:** John Akujobi  
**Website:** jakujobi.com  
**Email:** john@jakujobi.com

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
# Run pytest tests
pytest

# Run bash tests
./tests/run_tests.sh
```

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

## Configuration

The shell can be configured using YAML files. Configuration is loaded in this order:

1. `$AKUJOBIP1_CONFIG` environment variable (path to config file)
2. `./akujobip1.yaml` (current directory)
3. `~/.config/akujobip1/config.yaml` (user config)
4. Built-in defaults

See `examples/config.yaml` for all available options.

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

After installing, run `./setup.sh` again.

---

## License

This project is part of CSC456 Programming Assignment 1.
