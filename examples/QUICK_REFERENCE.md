# AkujobiP1Shell - Quick Reference

**Version:** 1.0.0 | **Author:** John Akujobi | **Date:** November 2025

---

## Installation

```bash
sudo apt install python3-venv    # Requires sudo
git clone https://github.com/jakujobi/AkujobiP1Shell.git
cd AkujobiP1Shell
./activate.sh                    # One command setup
```

---

## Running the Shell

```bash
akujobip1                        # Command name
python -m akujobip1              # Alternative
```

---

## Built-in Commands

| Command | Description | Example |
|---------|-------------|---------|
| `exit` | Exit the shell | `exit` |
| `cd [dir]` | Change directory | `cd /tmp` |
| `cd` | Go to home directory | `cd` |
| `cd -` | Go to previous directory | `cd -` |
| `pwd` | Print working directory | `pwd` |
| `help` | Show available commands | `help` |

---

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Ctrl+C` | Interrupt current command (shell continues) |
| `Ctrl+D` | Exit shell (same as `exit` command) |
| `Enter` | Execute command |

---

## Wildcards

| Pattern | Matches | Example |
|---------|---------|---------|
| `*` | Zero or more characters | `*.txt` → `file1.txt file2.txt` |
| `?` | Exactly one character | `file?.txt` → `file1.txt` |
| `[abc]` | One character from set | `[abc]*.py` → `a.py b.py` |
| `[a-z]` | One character from range | `file[1-3].txt` → `file1.txt` |

**Note:** Quote wildcards to use literally: `echo "*.txt"` → `*.txt`

---

## Quotes

| Type | Behavior | Example |
|------|----------|---------|
| Double `"..."` | Preserves spaces | `echo "hello world"` → `hello world` |
| Single `'...'` | Preserves everything | `echo 'hello world'` → `hello world` |
| Backslash `\` | Escapes next character | `echo hello\ world` → `hello world` |

---

## Exit Codes

| Code | Meaning | Example |
|------|---------|---------|
| `0` | Success | `ls` successful |
| `1-125` | Command-specific errors | `grep` no match = 1 |
| `126` | Permission denied | Cannot execute file |
| `127` | Command not found | `badcmd` doesn't exist |
| `128+N` | Terminated by signal N | Ctrl+C = 130 (128+2) |

---

## Configuration Files

**Priority Order (highest to lowest):**

1. `$AKUJOBIP1_CONFIG` environment variable
2. `./akujobip1.yaml` current directory
3. `~/.config/akujobip1/config.yaml` user config
4. Built-in defaults

**Quick Config:**

```yaml
prompt:
  text: "$ "
exit:
  message: "Goodbye!"
execution:
  show_exit_codes: "on_failure"  # never, on_failure, always
```

---

## Common Commands

### Navigation
```bash
pwd                    # Show current directory
cd /path               # Change directory
cd                     # Go home
cd -                   # Go to previous directory
cd ..                  # Go up one level
```

### File Operations
```bash
ls                     # List files
ls -la                 # List all files (detailed)
cp source dest         # Copy file
mv old new             # Move/rename file
rm file                # Remove file
mkdir dir              # Create directory
```

### File Viewing
```bash
cat file.txt           # Display file
head file.txt          # First 10 lines
tail file.txt          # Last 10 lines
grep pattern file.txt  # Search in file
wc -l file.txt         # Count lines
```

### Wildcards
```bash
ls *.txt               # All .txt files
rm temp*               # Remove files starting with 'temp'
cp *.py backup/        # Copy all Python files
```

### Quoted Arguments
```bash
echo "hello world"     # Preserve spaces
cat "my file.txt"      # File name with spaces
mkdir "New Folder"     # Directory with spaces
```

---

## Configuration Options Reference

```yaml
# Prompt
prompt:
  text: "AkujobiP1> "

# Exit message
exit:
  message: "Bye!"

# Exit code display
execution:
  show_exit_codes: "on_failure"  # never | on_failure | always
  exit_code_format: "[Exit: {code}]"

# Wildcards
glob:
  enabled: true
  show_expansions: false

# Built-ins
builtins:
  cd:
    enabled: true
    show_pwd_after: false
  pwd:
    enabled: true
  help:
    enabled: true

# Error handling
errors:
  verbose: false  # Show full tracebacks

# Debug
debug:
  log_commands: false
  log_file: "~/.akujobip1.log"
  show_fork_pids: false
```

---

## Example Usage

### Basic Session
```bash
$ akujobip1
AkujobiP1> pwd
/home/user
AkujobiP1> cd /tmp
AkujobiP1> ls
file1.txt  file2.txt
AkujobiP1> exit
Bye!
```

### With Wildcards
```bash
AkujobiP1> ls *.py
test.py  main.py  utils.py
AkujobiP1> echo test*
test.py  test_data.txt
```

### With Quotes
```bash
AkujobiP1> echo "hello world"
hello world
AkujobiP1> printf "%s %s\n" "arg one" "arg two"
arg one arg two
```

---

## Troubleshooting

### Command Not Found
```bash
AkujobiP1> badcmd
badcmd: command not found
[Exit: 127]
```
**Fix:** Check spelling, verify command is installed, or use full path.

### Permission Denied
```bash
AkujobiP1> ./script.sh
./script.sh: Permission denied
[Exit: 126]
```
**Fix:** `chmod +x script.sh` to make executable.

### Directory Not Found
```bash
AkujobiP1> cd /badpath
cd: /badpath: No such file or directory
```
**Fix:** Check path spelling, use absolute path, or verify directory exists.

### Wildcard No Matches
```bash
AkujobiP1> ls *.txt
ls: cannot access '*.txt': No such file or directory
[Exit: 2]
```
**This is normal** - no .txt files exist in directory.

---

## Development

### Run Tests
```bash
pytest -v                         # Unit tests
pytest --cov=akujobip1            # With coverage
./tests/run_tests.sh              # Bash integration tests
```

### Code Quality
```bash
ruff check src/                   # Linting
black --check src/                # Format check
black src/                        # Auto-format
```

---

## Documentation

- **Main Report:** `docs/report.md` (20+ pages)
- **Architecture Diagrams:** `docs/diagrams/` (4 Mermaid diagrams)
- **Usage Guide:** `examples/USAGE_GUIDE.md` (detailed)
- **Configuration Examples:** `examples/*.yaml`
- **Sample Session:** `examples/sample_session.txt`
- **README:** `README.md`

---

## POSIX System Calls Used

| Call | Purpose | Used Where |
|------|---------|------------|
| `fork()` | Create child process | External commands |
| `execvp()` | Replace process image | Command execution |
| `waitpid()` | Wait for child | Parent waits for child |
| `chdir()` | Change directory | `cd` command |
| `getcwd()` | Get current directory | `pwd` command |

**References:** https://pubs.opengroup.org/onlinepubs/9699919799/

---

## Project Information

- **Course:** CSC456 - Operating Systems
- **Assignment:** Programming Assignment 1
- **Author:** John Akujobi
- **Email:** john@jakujobi.com
- **Website:** jakujobi.com
- **Version:** 1.0.0
- **GitHub:** https://github.com/jakujobi/AkujobiP1Shell

---

## Quick Facts

- **Lines of Code:** 1,091 (across 5 modules)
- **Tests:** 229 passing unit tests + 4 bash tests
- **Coverage:** 89%
- **Python Version:** 3.10+
- **Supported OS:** Linux (Ubuntu recommended)
- **License:** Academic Project - CSC456

---

**For detailed documentation, see `docs/report.md` or `examples/USAGE_GUIDE.md`**

**Last Updated:** November 2025

