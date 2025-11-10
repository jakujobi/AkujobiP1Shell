# Phase 2.5 Critical Issues and Bug Prevention

**Date:** 2025-11-10  
**Phase:** Main Shell Loop Implementation  
**Purpose:** Prevent critical bugs before they happen

---

## 🔴 CRITICAL ISSUE #1: Signal Handler Race Condition

### The Problem

**Custom SIGINT handlers in the parent can interfere with child process execution.**

### Wrong Implementation ❌

```python
import signal

def sigint_handler(signum, frame):
    print("\nUse 'exit' to quit")
    # This will run during waitpid() and could cause issues!

signal.signal(signal.SIGINT, sigint_handler)

while True:
    command_line = input("prompt> ")
    # If custom handler is active, it affects child processes
```

**Why this is wrong:**
1. Handler runs during `waitpid()` in executor
2. Can interrupt system calls unexpectedly
3. Child needs default handler for proper Ctrl+C behavior
4. Adds complexity with no benefit

### Correct Implementation ✅

```python
# NO custom signal handler needed!
# Just catch the exception

while True:
    try:
        command_line = input("prompt> ")
        # ... process command
    except KeyboardInterrupt:
        print()  # Newline after ^C
        continue  # Show new prompt
```

**Why this is correct:**
1. Python's default SIGINT behavior works perfectly
2. During `input()`: Raises KeyboardInterrupt → we catch it
3. During command execution: Signal goes to child → executor handles it
4. Simple and safe

### How Executor Already Handles This

**From executor.py line 73:**
```python
# CRITICAL: Reset signal handlers to default so child can be interrupted
signal.signal(signal.SIGINT, signal.SIG_DFL)
```

**The executor ALREADY resets signals in the child process.**  
**We don't need to do anything else.**

### Test Coverage

- `test_ctrl_c_during_input()` - Verify KeyboardInterrupt caught
- `test_ctrl_c_during_command()` - Verify child gets signal
- `test_no_custom_signal_handler()` - Verify we didn't add one

---

## 🔴 CRITICAL ISSUE #2: Exit Command Returns -1

### The Problem

**Exit command returns -1 to signal termination, not 0.**

This is intentional design from Phase 2.3.

### Wrong Implementation ❌

```python
builtin = get_builtin(args[0])
if builtin:
    builtin.execute(args, config)
    # Shell never exits because we didn't check return value!
```

**Result:** Shell never terminates when user types `exit`

### Correct Implementation ✅

```python
builtin = get_builtin(args[0])
if builtin:
    exit_code = builtin.execute(args, config)
    if exit_code == -1:
        # Exit command was executed
        return 0  # Shell terminates successfully
```

### Why -1 Instead of 0?

**From builtins.py design:**
- `0` = Command succeeded, continue shell
- `1-125` = Command failed, continue shell
- `-1` = Special signal: terminate shell
- Allows exit command to print "Bye!" before shell terminates

### The Exit Command Code

**From builtins.py line 56-60:**
```python
def execute(self, args: List[str], config: Dict[str, Any]) -> int:
    message = config.get('exit', {}).get('message', 'Bye!')
    print(message)
    return -1  # Signal shell to exit
```

### Test Coverage

- `test_exit_command_terminates_shell()` - Verify shell exits
- `test_exit_returns_zero()` - Verify cli() returns 0
- `test_exit_with_args()` - Verify args ignored

---

## 🔴 CRITICAL ISSUE #3: Empty Args List Causes IndexError

### The Problem

**Parser returns empty list `[]` for empty or invalid input.**

### Wrong Implementation ❌

```python
args = parse_command(command_line, config)
builtin = get_builtin(args[0])  # IndexError: list index out of range
```

**When this crashes:**
- User presses Enter on empty line
- User enters only whitespace
- Parser encounters unclosed quote

### Correct Implementation ✅

```python
args = parse_command(command_line, config)

# Check for empty list before accessing args[0]
if not args:
    continue  # Skip to next prompt

builtin = get_builtin(args[0])  # Safe now
```

### Why Parser Returns Empty List

**From parser.py lines 38-40:**
```python
# Handle empty or whitespace-only input
if not command_line or not command_line.strip():
    return []
```

**From parser.py lines 46-50:**
```python
except ValueError as e:
    # shlex can raise ValueError for unclosed quotes
    print(f"Parse error: {e}", file=sys.stderr)
    return []  # Return empty list on error
```

### Test Coverage

- `test_empty_input()` - Verify empty line handled
- `test_whitespace_only()` - Verify whitespace handled
- `test_unclosed_quote()` - Verify parse error handled
- `test_no_index_error()` - Verify no crashes

---

## 🔴 CRITICAL ISSUE #4: Config Keys Might Not Exist

### The Problem

**Config might be missing keys or be completely empty.**

### Wrong Implementation ❌

```python
prompt = config['prompt']['text']  # KeyError if 'prompt' missing
exit_msg = config['exit']['message']  # KeyError if 'exit' missing
```

**When this crashes:**
- Config file is malformed
- Config file is incomplete
- YAML parsing fails
- User provides custom minimal config

### Correct Implementation ✅

```python
# Use .get() with nested dictionaries
prompt = config.get('prompt', {}).get('text', 'AkujobiP1> ')
exit_msg = config.get('exit', {}).get('message', 'Bye!')
```

**How it works:**
1. `config.get('prompt', {})` returns `{}` if 'prompt' missing
2. `{}.get('text', 'AkujobiP1> ')` returns default if 'text' missing
3. Never crashes, always has a value

### Pattern from Other Modules

**Executor (line 55):**
```python
if config.get('debug', {}).get('show_fork_pids', False):
```

**Parser (lines 55-56):**
```python
if config.get('glob', {}).get('enabled', True):
```

**Builtins (line 56):**
```python
message = config.get('exit', {}).get('message', 'Bye!')
```

**All modules use this pattern. Shell must too.**

### Test Coverage

- `test_missing_prompt_config()` - Verify default used
- `test_missing_exit_config()` - Verify default used
- `test_empty_config()` - Verify shell works with `{}`
- `test_null_config()` - Verify shell works with None

---

## 🟡 MEDIUM ISSUE #1: Unexpected Exception in Main Loop

### The Problem

**Any unexpected exception in main loop crashes the shell.**

### Wrong Implementation ❌

```python
while True:
    command_line = input(prompt)
    args = parse_command(command_line, config)
    # Any exception here crashes shell
```

**If anything unexpected happens, shell terminates.**

### Correct Implementation ✅

```python
while True:
    try:
        command_line = input(prompt)
        args = parse_command(command_line, config)
        # ... rest of loop
    except EOFError:
        # Expected - Ctrl+D
        break
    except KeyboardInterrupt:
        # Expected - Ctrl+C
        print()
        continue
    except Exception as e:
        # Unexpected - defensive programming
        print(f"Shell error: {e}", file=sys.stderr)
        if config.get('errors', {}).get('verbose', False):
            import traceback
            traceback.print_exc()
        continue  # Keep shell running
```

**Why this matters:**
- Shell should be resilient
- Unexpected errors shouldn't crash shell
- User can still type `exit` to quit
- Defensive programming best practice

### Test Coverage

- `test_unexpected_error_continues_shell()` - Mock unexpected error
- `test_verbose_error_mode()` - Test traceback printing

---

## 🟡 MEDIUM ISSUE #2: EOFError vs KeyboardInterrupt

### The Problem

**Both are exceptions during input(), but behavior should differ.**

### Wrong Implementation ❌

```python
try:
    command_line = input(prompt)
except Exception:
    # Treating both the same!
    continue
```

**Result:** Ctrl+D doesn't exit shell

### Correct Implementation ✅

```python
try:
    command_line = input(prompt)
except EOFError:
    # Ctrl+D pressed - EXIT shell
    print()
    print(exit_message)
    return 0
except KeyboardInterrupt:
    # Ctrl+C pressed - CONTINUE shell
    print()
    continue
```

### Difference

| Signal | Exception | Behavior | Exit Shell? |
|--------|-----------|----------|-------------|
| Ctrl+C | KeyboardInterrupt | Cancel line, new prompt | No |
| Ctrl+D | EOFError | Print "Bye!", exit | Yes |

### Test Coverage

- `test_ctrl_c_continues_shell()` - Verify shell continues
- `test_ctrl_d_exits_shell()` - Verify shell exits
- `test_ctrl_d_prints_exit_message()` - Verify "Bye!" printed

---

## 🟢 MINOR ISSUE #1: Import Organization

### Best Practice

```python
# Standard library imports first
import os
import sys
from typing import Dict, Any

# Project imports
from akujobip1.config import load_config
from akujobip1.parser import parse_command
from akujobip1.builtins import get_builtin
from akujobip1.executor import execute_external_command
```

### Test Coverage

- Linter will catch import issues

---

## 🟢 MINOR ISSUE #2: Prompt Flush

### The Issue

**Prompt should be displayed immediately, not buffered.**

### Wrong Implementation ❌

```python
print("AkujobiP1> ", end='')
command_line = sys.stdin.readline()
```

**Problem:** Output might be buffered

### Correct Implementation ✅

```python
# input() handles flushing automatically
command_line = input(prompt)
```

**Python's `input()` function:**
- Writes prompt to stdout
- Flushes stdout automatically
- Reads from stdin
- Handles newline stripping
- Perfect for REPL loops

---

## Issue Priority Summary

### Must Fix Before Shipping

| Issue | Severity | Impact if Not Fixed |
|-------|----------|---------------------|
| #1: Signal Handler | CRITICAL | Child processes don't respond to Ctrl+C |
| #2: Exit Code Check | CRITICAL | Shell never exits |
| #3: Empty Args | CRITICAL | Shell crashes on empty input |
| #4: Config Keys | CRITICAL | Shell crashes on missing config |

### Should Fix (Defensive)

| Issue | Severity | Impact if Not Fixed |
|-------|----------|---------------------|
| #5: Unexpected Exception | MEDIUM | Shell crashes on rare errors |
| #6: EOF vs Interrupt | MEDIUM | Ctrl+D doesn't exit |

### Nice to Have

| Issue | Severity | Impact if Not Fixed |
|-------|----------|---------------------|
| #7: Import Order | MINOR | Linter warning |
| #8: Prompt Flush | MINOR | None (input() handles it) |

---

## Code Review Checklist

Before committing, verify:

### Critical Items

- [ ] NO custom signal handlers (no `signal.signal()` calls)
- [ ] Exit code checked: `if exit_code == -1:`
- [ ] Empty args checked: `if not args:`
- [ ] Config accessed with `.get()`
- [ ] All exceptions caught appropriately

### Required Exception Handling

```python
while True:
    try:
        # Main loop code
    except EOFError:
        # Exit shell
        pass
    except KeyboardInterrupt:
        # Continue shell
        pass
    except Exception:
        # Defensive - continue shell
        pass
```

### Test Coverage

- [ ] All critical issues have tests
- [ ] All medium issues have tests
- [ ] Edge cases covered
- [ ] Bash tests simulated

---

## Testing Strategy for Critical Issues

### Issue #1: Signal Handler

```python
def test_no_custom_signal_handler():
    """Verify we don't install custom SIGINT handler."""
    import signal
    original_handler = signal.getsignal(signal.SIGINT)
    
    config = get_default_config()
    # Don't actually run shell, just verify imports don't change handler
    from akujobip1.shell import cli
    
    assert signal.getsignal(signal.SIGINT) == original_handler
```

### Issue #2: Exit Code

```python
def test_exit_command_terminates_shell(mock_input_sequence):
    """Verify exit command terminates shell."""
    config = get_default_config()
    
    with patch('builtins.input', mock_input_sequence('exit')):
        exit_code = run_shell(config)
    
    assert exit_code == 0  # Shell exited successfully
```

### Issue #3: Empty Args

```python
def test_empty_input_no_crash(mock_input_sequence):
    """Verify empty input doesn't crash."""
    config = get_default_config()
    
    with patch('builtins.input', mock_input_sequence('', 'exit')):
        exit_code = run_shell(config)
    
    assert exit_code == 0  # No crash
```

### Issue #4: Config Keys

```python
def test_missing_config_keys():
    """Verify missing config keys don't crash."""
    config = {}  # Empty config
    
    with patch('builtins.input', side_effect=['exit']):
        exit_code = run_shell(config)
    
    assert exit_code == 0  # No crash
```

---

## Final Checklist Before Marking Complete

### Implementation

- [ ] No custom signal handlers
- [ ] Exit code -1 checked
- [ ] Empty args checked
- [ ] Config accessed safely

### Testing

- [ ] All critical issues tested
- [ ] All bash tests simulated
- [ ] Coverage >= 95%
- [ ] No test failures

### Quality

- [ ] No linter errors
- [ ] Code formatted
- [ ] Documentation complete
- [ ] Changelog updated

---

**Remember:** 
- Keep it simple
- Don't over-engineer
- Test the critical paths
- Follow the patterns from Phase 2.1-2.4

**You got this! 🚀**

