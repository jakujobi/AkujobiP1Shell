# AkujobiP1Shell - Complete Demo Guide

**Author:** John Akujobi  
**Version:** 1.0.0  
**Course:** CSC456 - Operating Systems  
**Date:** November 2025

---

## Overview

This guide provides a complete demonstration script for presenting AkujobiP1Shell. Use this for:
- Live demonstrations
- Video recordings
- Instructor presentations
- Practice runs before submission

**Estimated Demo Time:** 10-15 minutes

---

## Pre-Demo Setup

### 1. Verify Installation

```bash
cd /home/ja/dev/AkujobiP1Shell
./activate.sh
source venv/bin/activate
python -c "import akujobip1; print(f'Version: {akujobip1.__version__}')"
```

**Expected Output:** `Version: 1.0.0`

### 2. Run Tests (Optional - for confidence)

```bash
pytest -q
```

**Expected:** `229 passed in ~0.8s`

### 3. Prepare Terminal

- Clear terminal: `clear`
- Set comfortable font size
- Position terminal for screen recording
- Have this guide visible on second monitor

---

## Demo Script: Part 1 - Basic Functionality (3 minutes)

### Section 1.1: Shell Startup

**Say:** "Let me start the shell and show you the basic interface."

```bash
akujobip1
```

**Expected Output:**
```
AkujobiP1>
```

**Explain:** "The shell displays a configurable prompt and waits for commands. This is the Read-Eval-Print Loop, or REPL."

### Section 1.2: Simple Commands

**Say:** "First, let's run some simple commands to show basic functionality."

```bash
pwd
```

**Explain:** "pwd is a built-in command that uses the POSIX getcwd() system call."

```bash
ls
```

**Explain:** "ls is an external command. The shell uses fork() to create a child process, execvp() to replace it with ls, and waitpid() to wait for completion."

```bash
echo "Hello from AkujobiP1Shell"
```

**Expected Output:** `Hello from AkujobiP1Shell`

**Explain:** "Notice how quotes are handled properly - the entire string is passed as one argument."

### Section 1.3: Commands with Arguments

**Say:** "The shell properly handles multiple arguments."

```bash
ls -la
```

**Explain:** "Multiple arguments are parsed and passed to the command. The -la flags work as expected."

```bash
echo one two three
```

**Expected Output:** `one two three`

---

## Demo Script: Part 2 - Built-in Commands (3 minutes)

### Section 2.1: help Command

**Say:** "The shell has four built-in commands. Let me show you the help."

```bash
help
```

**Expected Output:**
```
Built-in commands:
  exit       Exit the shell
  cd [dir]   Change directory (cd - for previous, cd for home)
  pwd        Print working directory
  help       Show this help message
```

**Explain:** "Built-ins execute directly in the shell process without forking. This is necessary for commands like cd that need to change the shell's own state."

### Section 2.2: cd Command Features

**Say:** "The cd command demonstrates why built-ins are necessary."

```bash
pwd
```

*Note the current directory*

```bash
cd /tmp
```

```bash
pwd
```

**Expected Output:** `/tmp`

**Explain:** "cd uses POSIX chdir() to change the shell's working directory. If this were external, only the child would change directories."

**Say:** "cd has some nice features:"

```bash
cd -
```

```bash
pwd
```

**Expected Output:** *(back to original directory)*

**Explain:** "cd - returns to the previous directory, just like bash."

```bash
cd
```

```bash
pwd
```

**Expected Output:** `/home/ja` (or your home directory)

**Explain:** "cd with no arguments goes to home directory."

**Return to project:**
```bash
cd /home/ja/dev/AkujobiP1Shell
```

---

## Demo Script: Part 3 - Advanced Features (4 minutes)

### Section 3.1: Wildcard Expansion

**Say:** "The shell supports wildcard expansion using Python's glob module."

```bash
cd src/akujobip1
```

```bash
ls *.py
```

**Expected Output:**
```
__init__.py  __main__.py  builtins.py  config.py  executor.py  parser.py  shell.py
```

**Explain:** "The asterisk is expanded to match all .py files before ls sees the arguments."

```bash
echo *.py
```

**Expected Output:** *(same list of files)*

**Explain:** "Wildcards work with any command."

**Try a pattern with no matches:**
```bash
ls *.nonexistent
```

**Expected Output:**
```
ls: cannot access '*.nonexistent': No such file or directory
[Exit: 2]
```

**Explain:** "When no files match, the literal pattern is preserved. Also notice the exit code display."

```bash
cd ../..
```

### Section 3.2: Quote Handling

**Say:** "The shell properly handles quoted arguments using Python's shlex module."

```bash
echo "hello world"
```

**Expected Output:** `hello world`

**Explain:** "Spaces inside quotes are preserved."

```bash
echo 'single quotes work too'
```

**Expected Output:** `single quotes work too`

**Say:** "Let's show this with a more complex example:"

```bash
printf "%s %s\n" "first arg" "second arg"
```

**Expected Output:**
```
first arg second arg
```

**Explain:** "Each quoted string is treated as a single argument, even with spaces."

### Section 3.3: Error Handling

**Say:** "The shell handles errors gracefully and doesn't crash."

**Try a non-existent command:**
```bash
badcommand
```

**Expected Output:**
```
badcommand: command not found
[Exit: 127]
```

**Explain:** "Exit code 127 is the POSIX standard for 'command not found'. The shell continues running."

**Try an invalid cd:**
```bash
cd /invalid/path
```

**Expected Output:**
```
cd: /invalid/path: No such file or directory
```

**Explain:** "Built-in commands also have proper error handling. The shell continues."

---

## Demo Script: Part 4 - POSIX System Calls (3 minutes)

### Section 4.1: Fork/Exec/Wait Pattern

**Say:** "Let me show you the core POSIX system calls in action. First, I'll enable debug mode."

**Exit and create a verbose config:**
```bash
exit
```

```bash
cat > demo_config.yaml << EOF
execution:
  show_exit_codes: "always"
debug:
  show_fork_pids: true
EOF
```

```bash
AKUJOBIP1_CONFIG=demo_config.yaml akujobip1
```

**Say:** "Now every command shows the process details."

```bash
ls
```

**Expected Output:** *(something like)*
```
[About to fork for: ls]
[Forked child PID: 12345]
README.md  docs/  examples/  src/  tests/  venv/
[Exit: 0]
```

**Explain:** "Watch the sequence:
1. Shell calls fork() - creates duplicate process
2. Child process (PID shown) is created
3. Child calls execvp() - replaces itself with ls
4. ls runs and exits with code 0
5. Parent calls waitpid() - extracts exit status
6. Exit code is displayed

This is the classic Unix process model."

### Section 4.2: Exit Codes

**Say:** "Let's see different exit codes."

```bash
true
```

**Expected Output:** `[Exit: 0]`

**Explain:** "0 means success."

```bash
false
```

**Expected Output:** `[Exit: 1]`

**Explain:** "Non-zero means failure."

```bash
ls /nonexistent
```

**Expected Output:**
```
ls: cannot access '/nonexistent': No such file or directory
[Exit: 2]
```

**Explain:** "Different programs use different error codes. 2 is ls's error code."

---

## Demo Script: Part 5 - Signal Handling (2 minutes)

### Section 5.1: Ctrl+C (SIGINT)

**Say:** "The shell properly handles signals. Watch what happens with Ctrl+C."

```bash
sleep 10
```

**Wait 2 seconds, then press Ctrl+C**

**Expected Output:**
```
^C
[Terminated by signal 2]
[Exit: 130]
```

**Explain:** "The signal (SIGINT = 2) goes to the child process, not the shell. The shell detects signal termination and shows exit code 130 (128 + signal number). The shell itself continues running."

```bash
echo "still works"
```

**Expected Output:**
```
still works
[Exit: 0]
```

**Explain:** "The shell is still running normally."

### Section 5.2: Ctrl+D (EOF)

**Say:** "Ctrl+D exits the shell gracefully."

**Press Ctrl+D**

**Expected Output:**
```
Bye!
```

**Explain:** "This is the clean way to exit, equivalent to the exit command."

---

## Demo Script: Part 6 - Configuration (2 minutes)

### Section 6.1: Show Configuration

**Say:** "The shell is highly configurable. Let me show you a custom configuration."

```bash
cat > custom_demo.yaml << EOF
prompt:
  text: "[demo]$ "
exit:
  message: "Demo complete!"
execution:
  show_exit_codes: "never"
EOF
```

```bash
AKUJOBIP1_CONFIG=custom_demo.yaml akujobip1
```

**Expected Output:**
```
[demo]$
```

**Explain:** "Notice the custom prompt."

```bash
ls
```

**Expected Output:** *(file list, no exit code)*

**Explain:** "Exit codes are hidden with show_exit_codes: never."

```bash
exit
```

**Expected Output:**
```
Demo complete!
```

**Explain:** "Custom exit message configured in YAML."

---

## Demo Script: Part 7 - Quality Metrics (1 minute)

**Say:** "Let me show you the testing and quality assurance."

```bash
pytest -v 2>&1 | head -30
```

**Explain:** "229 unit tests covering all functionality."

```bash
pytest --cov=akujobip1 --cov-report=term-missing 2>&1 | tail -15
```

**Explain:** "89% code coverage - very high for a systems project."

```bash
ruff check src/
```

**Expected Output:** `All checks passed!`

**Explain:** "Zero linting errors."

---

## Demo Conclusion

**Say:** "To summarize, AkujobiP1Shell demonstrates:

1. **POSIX Process Management**
   - fork() to create child processes
   - execvp() to execute commands
   - waitpid() to synchronize and get exit status

2. **Built-in Commands**
   - exit, cd, pwd, help
   - Direct execution without forking
   - POSIX chdir() and getcwd() system calls

3. **Robust Parsing**
   - Quote handling with shlex
   - Wildcard expansion with glob
   - Proper argument tokenization

4. **Signal Handling**
   - Ctrl+C interrupts commands, not shell
   - Ctrl+D exits gracefully
   - Proper signal routing to child processes

5. **Configuration**
   - YAML-based configuration
   - Priority-based merging
   - Customizable behavior

6. **Quality**
   - 229 passing tests
   - 89% code coverage
   - Zero linting errors
   - Professional documentation

The implementation is complete, well-tested, and production-ready."

---

## Troubleshooting During Demo

### If command doesn't work:

1. **Check you're in the shell:** Look for `AkujobiP1>` prompt
2. **Check virtual environment:** Run `which akujobip1`
3. **Restart shell:** `exit` then `akujobip1`

### If demo goes wrong:

1. **Stay calm:** Shell is robust, just restart
2. **Show error handling:** Mistakes demonstrate robustness
3. **Reference documentation:** Open `docs/report.md`

### Quick recovery:

```bash
cd /home/ja/dev/AkujobiP1Shell
source venv/bin/activate
akujobip1
```

---

## Recording the Demo

### Video Recording Setup

1. **Screen Recording Tool:**
   - Linux: SimpleScreenRecorder, OBS Studio, or Kazam
   - Set to record terminal only
   - 1080p or higher resolution

2. **Terminal Setup:**
   ```bash
   # Increase font size for readability
   # Clear screen
   clear
   # Show working directory
   pwd
   ```

3. **Recording Checklist:**
   - [ ] Microphone working (if narrating)
   - [ ] Terminal font size large enough
   - [ ] No private information visible
   - [ ] Demo script accessible on second monitor

### Screenshot Capture

For the 12 required screenshots, capture:

1. **Shell startup** - `akujobip1` prompt
2. **Simple commands** - `pwd`, `ls`, `echo`
3. **Multiple arguments** - `ls -la`
4. **Quoted arguments** - `echo "hello world"`
5. **Built-in commands** - `help` output
6. **Wildcard expansion** - `ls *.py`
7. **Error handling** - command not found
8. **Exit codes** - with `show_exit_codes: always`
9. **Signal handling** - Ctrl+C during sleep
10. **Configuration** - custom prompt
11. **Test results** - `pytest` output
12. **CI/CD** - GitHub Actions passing

**Capture command:**
```bash
gnome-screenshot -w --file="01_startup.png"  # For current window
# Or use your preferred screenshot tool
```

---

## Post-Demo Cleanup

```bash
# Remove demo config files
rm -f demo_config.yaml custom_demo.yaml

# Verify project state
cd /home/ja/dev/AkujobiP1Shell
pytest -q
git status

# All good? Ready for submission!
```

---

## Quick Demo (5-minute version)

For a short demo, focus on:

1. **Start shell** - `akujobip1`
2. **Built-ins** - `pwd`, `cd /tmp`, `cd -`, `help`
3. **External commands** - `ls`, `echo "test"`
4. **Wildcards** - `ls *.py`
5. **Error handling** - `badcommand`
6. **Signal handling** - `sleep 5` then Ctrl+C
7. **Exit** - `exit`

**Script:**
```bash
akujobip1
pwd
cd /tmp && pwd
cd -
ls *.py
badcommand  # Shows error handling
sleep 5  # Press Ctrl+C after 2 seconds
exit
```

---

## Notes for Live Presentation

1. **Practice First:** Run through 2-3 times before live demo
2. **Have Backup:** Keep this document open during demo
3. **Explain As You Go:** Don't just type, explain each step
4. **Show Documentation:** Reference `docs/report.md` for details
5. **Be Ready for Questions:** Know the POSIX system calls well

---

**Demo preparation complete! You're ready to present AkujobiP1Shell professionally.**

**Last Updated:** November 10, 2025  
**Author:** John Akujobi  
**Course:** CSC456 - Operating Systems

