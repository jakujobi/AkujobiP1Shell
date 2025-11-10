# AkujobiP1Shell - Complete Usage Guide

**Author:** John Akujobi  
**Version:** 1.0.0  
**Date:** November 2025

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Basic Usage](#basic-usage)
3. [Built-in Commands](#built-in-commands)
4. [Command Parsing](#command-parsing)
5. [Configuration](#configuration)
6. [Advanced Usage](#advanced-usage)
7. [Tips and Tricks](#tips-and-tricks)
8. [Troubleshooting](#troubleshooting)

---

## Getting Started

### Installation

```bash
# Install system dependency (requires sudo)
sudo apt install python3-venv

# Clone and setup
git clone https://github.com/jakujobi/AkujobiP1Shell.git
cd AkujobiP1Shell
./activate.sh
```

### First Run

```bash
$ akujobip1
AkujobiP1>
```

The shell is now ready for commands!

### Exiting the Shell

Two ways to exit:

1. **exit command:**
   ```
   AkujobiP1> exit
   Bye!
   ```

2. **Ctrl+D (EOF):**
   ```
   AkujobiP1> ^D
   Bye!
   ```

---

## Basic Usage

### Running Commands

Simply type a command and press Enter:

```bash
AkujobiP1> pwd
/home/user

AkujobiP1> ls
file1.txt  file2.txt  directory/

AkujobiP1> echo hello
hello
```

### Commands with Arguments

Pass arguments separated by spaces:

```bash
AkujobiP1> ls -la
# Long listing with all files

AkujobiP1> cp file1.txt file2.txt
# Copy file1.txt to file2.txt

AkujobiP1> mkdir new_directory
# Create directory
```

### Command Not Found

If a command doesn't exist:

```bash
AkujobiP1> badcommand
badcommand: command not found
[Exit: 127]
```

The shell continues - it doesn't crash.

---

## Built-in Commands

Built-in commands are executed directly by the shell without creating a new process.

### exit - Exit the Shell

**Syntax:** `exit`

**Description:** Terminates the shell and prints the configured exit message.

**Example:**
```bash
AkujobiP1> exit
Bye!
```

**Notes:**
- Also triggered by Ctrl+D (EOF)
- Exit message configurable in config file

### cd - Change Directory

**Syntax:** `cd [directory]`

**Description:** Changes the current working directory.

**Forms:**

1. **cd** (no arguments) - Go to home directory:
   ```bash
   AkujobiP1> cd
   # Now in /home/user
   ```

2. **cd /path** - Go to specific directory:
   ```bash
   AkujobiP1> cd /tmp
   # Now in /tmp
   ```

3. **cd -** - Go to previous directory:
   ```bash
   AkujobiP1> cd /tmp
   AkujobiP1> cd /var
   AkujobiP1> cd -
   # Back to /tmp
   ```

**Error Handling:**

```bash
AkujobiP1> cd /nonexistent
cd: /nonexistent: No such file or directory

AkujobiP1> cd file.txt
cd: file.txt: Not a directory
```

**Why Built-in:**
`cd` must be a built-in because it needs to change the shell's own working directory. If it were an external command, it would only change the child process's directory.

### pwd - Print Working Directory

**Syntax:** `pwd`

**Description:** Displays the absolute path of the current working directory.

**Example:**
```bash
AkujobiP1> pwd
/home/user/dev/AkujobiP1Shell
```

**Notes:**
- Uses POSIX getcwd() system call
- Always shows absolute path
- Could be external, but faster as built-in

### help - Show Available Commands

**Syntax:** `help`

**Description:** Displays list of available built-in commands with brief descriptions.

**Example:**
```bash
AkujobiP1> help
Built-in commands:
  exit       Exit the shell
  cd [dir]   Change directory (cd - for previous, cd for home)
  pwd        Print working directory
  help       Show this help message
```

---

## Command Parsing

### Quote Handling

The shell properly handles quoted arguments.

#### Double Quotes

Preserve spaces and most special characters:

```bash
AkujobiP1> echo "hello world"
hello world

AkujobiP1> echo "multiple    spaces    preserved"
multiple    spaces    preserved
```

#### Single Quotes

Preserve everything literally:

```bash
AkujobiP1> echo 'hello world'
hello world

AkujobiP1> echo '$VAR is not expanded'
$VAR is not expanded
```

#### Mixed Quotes

Different quote types in same command:

```bash
AkujobiP1> printf "%s %s\n" "double" 'single'
double single
```

### Wildcard Expansion

The shell expands wildcards before executing commands.

#### Asterisk (*)

Matches zero or more characters:

```bash
AkujobiP1> ls *.txt
file1.txt  file2.txt  readme.txt

AkujobiP1> echo test*
test.py  test_file.txt  testing.md
```

#### Question Mark (?)

Matches exactly one character:

```bash
AkujobiP1> ls file?.txt
file1.txt  file2.txt  file3.txt

AkujobiP1> echo test?.py
test1.py  test2.py
```

#### Character Set ([...])

Matches one character from set:

```bash
AkujobiP1> ls file[123].txt
file1.txt  file2.txt  file3.txt

AkujobiP1> ls [abc]*.py
a_file.py  b_script.py  c_module.py
```

#### Character Range ([a-z])

Matches one character from range:

```bash
AkujobiP1> ls file[a-c].txt
filea.txt  fileb.txt  filec.txt
```

#### No Matches

If wildcard doesn't match anything, the literal is preserved:

```bash
AkujobiP1> ls *.nonexistent
ls: cannot access '*.nonexistent': No such file or directory
```

#### Disabling Wildcards

Quote wildcards to use them literally:

```bash
AkujobiP1> echo "*.txt"
*.txt

AkujobiP1> echo '*.py'
*.py
```

### Escape Sequences

The shell supports backslash escapes:

```bash
AkujobiP1> echo hello\ world
hello world

AkujobiP1> echo "quote: \"hello\""
quote: "hello"
```

---

## Configuration

### Configuration Files

Configuration is loaded in priority order:

1. **$AKUJOBIP1_CONFIG** (highest priority)
   ```bash
   export AKUJOBIP1_CONFIG="/path/to/config.yaml"
   akujobip1
   ```

2. **./akujobip1.yaml** (project config)
   ```bash
   # Create in current directory
   cp examples/minimal_config.yaml akujobip1.yaml
   akujobip1
   ```

3. **~/.config/akujobip1/config.yaml** (user config)
   ```bash
   mkdir -p ~/.config/akujobip1
   cp examples/minimal_config.yaml ~/.config/akujobip1/config.yaml
   akujobip1
   ```

4. **Built-in defaults** (lowest priority)

### Configuration Options

See `examples/` directory for complete configuration examples:

- `minimal_config.yaml` - Simple, essential settings
- `verbose_config.yaml` - Maximum visibility for debugging
- `quiet_config.yaml` - Minimal output
- `custom_config.yaml` - Personalized setup

### Common Customizations

#### Change Prompt

```yaml
prompt:
  text: "$ "
```

#### Always Show Exit Codes

```yaml
execution:
  show_exit_codes: "always"
```

#### Custom Exit Message

```yaml
exit:
  message: "See you later!"
```

#### Show Directory After cd

```yaml
builtins:
  cd:
    show_pwd_after: true
```

---

## Advanced Usage

### Exit Codes

The shell displays exit codes based on configuration.

#### Exit Code Meanings

- **0**: Success
- **1-125**: Command-specific errors
- **126**: Permission denied (cannot execute)
- **127**: Command not found
- **128+N**: Terminated by signal N

#### Configuration

```yaml
execution:
  show_exit_codes: "on_failure"  # never, on_failure, always
  exit_code_format: "[Exit: {code}]"
```

#### Examples

```bash
# Success (shown if "always")
AkujobiP1> ls
file.txt
[Exit: 0]

# Command not found
AkujobiP1> badcmd
badcmd: command not found
[Exit: 127]

# Command error
AkujobiP1> ls /nonexistent
ls: cannot access '/nonexistent': No such file or directory
[Exit: 2]

# Signal termination (Ctrl+C)
AkujobiP1> sleep 10
^C
[Terminated by signal 2]
[Exit: 130]
```

### Signal Handling

#### Ctrl+C (SIGINT)

During command execution:
- Terminates the running command
- Shell continues with new prompt
- Does NOT terminate the shell

```bash
AkujobiP1> sleep 30
^C
[Terminated by signal 2]
[Exit: 130]
AkujobiP1> echo "still works"
still works
```

During input:
- Cancels current line
- Shows new prompt
- Shell continues

```bash
AkujobiP1> some incomplete comma^C
AkujobiP1>
```

#### Ctrl+D (EOF)

- Exits the shell gracefully
- Shows exit message
- Same as `exit` command

### Empty Input

The shell handles empty input gracefully:

```bash
AkujobiP1>
# Just shows new prompt

AkujobiP1>    
# Whitespace-only also ignored
```

---

## Tips and Tricks

### Quick Navigation

```bash
# Go home
AkujobiP1> cd

# Go to previous directory
AkujobiP1> cd -

# Go up one level
AkujobiP1> cd ..

# Go up two levels
AkujobiP1> cd ../..
```

### Efficient File Operations

```bash
# Copy all Python files
AkujobiP1> cp *.py backup/

# List all files starting with 'test'
AkujobiP1> ls test*

# Remove all temporary files
AkujobiP1> rm *.tmp
```

### Working with Spaces in Names

```bash
# Use quotes for file names with spaces
AkujobiP1> cat "my file.txt"

# Or escape spaces
AkujobiP1> cat my\ file.txt

# Create directory with spaces
AkujobiP1> mkdir "My Documents"
```

### Checking Exit Codes

Enable to always see them:

```yaml
# In config file
execution:
  show_exit_codes: "always"
```

Then:
```bash
AkujobiP1> test -f file.txt
[Exit: 0]  # File exists

AkujobiP1> test -f nonexistent
[Exit: 1]  # File doesn't exist
```

### Using Different Configs

```bash
# Project-specific config
cd ~/project
cat > akujobip1.yaml << EOF
prompt:
  text: "[project]$ "
EOF
akujobip1

# Or via environment
export AKUJOBIP1_CONFIG=~/my-config.yaml
akujobip1
```

---

## Troubleshooting

### Command Not Found

**Problem:**
```bash
AkujobiP1> mycommand
mycommand: command not found
[Exit: 127]
```

**Solutions:**
1. Check if command is installed: `which mycommand`
2. Check PATH: `echo $PATH`
3. Use full path: `/usr/bin/mycommand`
4. Install the package: `sudo apt install package-name`

### Permission Denied

**Problem:**
```bash
AkujobiP1> ./script.sh
./script.sh: Permission denied
[Exit: 126]
```

**Solutions:**
1. Make file executable: `chmod +x script.sh`
2. Run with interpreter: `bash script.sh`
3. Check file ownership: `ls -l script.sh`

### cd Doesn't Work

**Problem:**
```bash
AkujobiP1> cd /some/path
cd: /some/path: No such file or directory
```

**Solutions:**
1. Check if directory exists: `ls /some/path`
2. Check for typos in path
3. Use absolute path instead of relative
4. Check permissions: `ls -ld /some/path`

### Wildcards Not Expanding

**Problem:**
```bash
AkujobiP1> ls *.txt
ls: cannot access '*.txt': No such file or directory
```

**This is normal!** It means no .txt files exist in current directory.

**To verify:**
```bash
AkujobiP1> ls -a
# Shows all files including hidden ones
```

### Shell Hangs or Freezes

**Problem:** Command seems stuck.

**Solutions:**
1. Press Ctrl+C to interrupt command
2. Check if command is waiting for input
3. Check if command is actually running (long operation)

### Configuration Not Loading

**Problem:** Changes to config file aren't applied.

**Solutions:**
1. Check file location (priority order)
2. Validate YAML syntax: `python3 -c "import yaml; yaml.safe_load(open('akujobip1.yaml'))"`
3. Check for warnings when shell starts
4. Verify file permissions: `ls -l akujobip1.yaml`

### Exit Codes Not Showing

**Problem:** No exit codes displayed.

**Solution:**

Check configuration:
```yaml
execution:
  show_exit_codes: "never"  # Change to "on_failure" or "always"
```

---

## Common Patterns

### File Management

```bash
# List all files
AkujobiP1> ls -la

# Copy files
AkujobiP1> cp source.txt dest.txt

# Move/rename files
AkujobiP1> mv old.txt new.txt

# Remove files
AkujobiP1> rm unwanted.txt

# Create directory
AkujobiP1> mkdir new_folder
```

### Directory Navigation

```bash
# Show where you are
AkujobiP1> pwd

# Go somewhere
AkujobiP1> cd /path/to/directory

# Go back
AkujobiP1> cd -

# Go home
AkujobiP1> cd
```

### Text Processing

```bash
# Display file
AkujobiP1> cat file.txt

# Search in files
AkujobiP1> grep pattern file.txt

# Count lines
AkujobiP1> wc -l file.txt

# Display first lines
AkujobiP1> head file.txt

# Display last lines
AkujobiP1> tail file.txt
```

---

## Getting Help

### In-Shell Help

```bash
AkujobiP1> help
```

### Documentation

- **Main Report**: `docs/report.md`
- **Architecture Diagrams**: `docs/diagrams/`
- **README**: `README.md`
- **Quick Reference**: `examples/QUICK_REFERENCE.md`

### External Resources

- **POSIX Standards**: https://pubs.opengroup.org/onlinepubs/9699919799/
- **Python os Module**: https://docs.python.org/3/library/os.html
- **Project GitHub**: https://github.com/jakujobi/AkujobiP1Shell

### Contact

- **Email**: john@jakujobi.com
- **Website**: jakujobi.com

---

**Document Version:** 1.0  
**Last Updated:** November 2025  
**Author:** John Akujobi

