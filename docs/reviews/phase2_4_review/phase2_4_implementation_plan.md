# Phase 2.4: Process Executor Implementation Plan

**Date:** 2025-11-10  
**Author:** John Akujobi  
**Status:** Planning

---

## 1. Requirements Analysis

### Primary Function: execute_external_command()

**Purpose:** Execute external commands using POSIX fork/exec/wait system calls

**Requirements:**
- Create child process using `os.fork()`
- Child replaces itself with command using `os.execvp()`
- Parent waits for child completion using `os.waitpid()`
- Handle all error conditions gracefully
- Display exit codes based on configuration
- Return proper exit code to caller
- Support signal handling (Ctrl+C kills child, not parent)

### Secondary Function: display_exit_status()

**Purpose:** Display exit status based on configuration settings

**Requirements:**
- Check if process exited normally or was signaled
- Display exit code only if configured (never/on_failure/always)
- Format output using configured format string
- Distinguish between normal exit and signal termination
- Handle edge cases (stopped processes, continued processes)

### Integration Requirements

**With Configuration System (Phase 2.1):**
- `config['execution']['show_exit_codes']` - Controls when to display (never/on_failure/always)
- `config['execution']['exit_code_format']` - Format string for exit code display
- `config['debug']['show_fork_pids']` - Whether to show child PIDs for debugging
- `config['errors']['verbose']` - Whether to show detailed error messages

**With Parser (Phase 2.2):**
- Receives `List[str]` with args[0] as command name
- Must handle empty lists gracefully (though parser shouldn't send empty)
- Parser guarantees no None values in list

**With Built-ins (Phase 2.3):**
- Should NEVER be called for built-in commands (handled by shell loop)
- Built-ins return -1 for exit, executor should never see this
- No overlap in functionality

**With Future Shell Loop (Phase 2.5):**
- Will be called after checking if command is built-in
- Must return int exit code
- Should never raise exceptions (catch and return error code)
- Should handle Ctrl+C gracefully (child dies, parent continues)

---

## 2. Code Tracing & Integration Analysis

### 2.1 Existing Code Patterns

**Error Handling Pattern (from builtins.py):**
```python
try:
    # Operation
    os.chdir(target)
except SpecificError:
    print(f"command: {detail}: Error message", file=sys.stderr)
    return 1
```

**Configuration Access Pattern (from all modules):**
```python
# Safe nested access with defaults
config.get('execution', {}).get('show_exit_codes', 'on_failure')
```

**Type Hints Pattern (from all modules):**
```python
def function(args: List[str], config: Dict[str, Any]) -> int:
    """Docstring with Args, Returns, Examples."""
    pass
```

### 2.2 Critical Integration Points

**Point 1: Configuration Keys**
```python
# From config.py get_default_config():
'execution': {
    'show_exit_codes': 'on_failure',  # never, on_failure, always
    'exit_code_format': '[Exit: {code}]'
},
'debug': {
    'show_fork_pids': False
}
```
✅ **Safe to use** - These keys exist in default config

**Point 2: Parser Output**
```python
# From parser.py parse_command():
# Returns: List[str] or []
# Never returns None
# args[0] is always command name if list is non-empty
```
✅ **Safe to use** - Well-defined contract

**Point 3: Signal Handling**
```python
# Child must reset signal handlers:
signal.signal(signal.SIGINT, signal.SIG_DFL)
```
⚠️ **Critical** - Without this, Ctrl+C will kill parent shell

### 2.3 Potential Issues & Bugs Identified

#### Issue 1: Fork Failure Edge Cases
**Problem:** `os.fork()` can fail if system resource limits reached
**Impact:** Would raise OSError
**Solution:** Wrap in try/except, return error code 1
**Test:** Mock fork to raise OSError

#### Issue 2: Zombie Processes
**Problem:** If we don't wait for child, it becomes zombie
**Impact:** System resource leak
**Solution:** Always call waitpid, even on errors
**Test:** Verify waitpid is called in all code paths

#### Issue 3: Race Condition in Signal Setup
**Problem:** If child receives SIGINT before resetting handler, parent might die
**Impact:** Shell exits unexpectedly
**Solution:** Reset signal handlers immediately after fork in child
**Test:** Difficult to test - review code carefully

#### Issue 4: Windows Compatibility
**Problem:** `os.fork()` doesn't exist on Windows
**Impact:** ImportError or AttributeError on Windows
**Solution:** Check platform, use subprocess as fallback (or just document Linux-only)
**Test:** Skip tests on Windows or test fallback

#### Issue 5: Exit Status Extraction
**Problem:** waitpid returns encoded status, need POSIX macros to extract
**Impact:** Wrong exit codes displayed
**Solution:** Use os.WIFEXITED(), os.WEXITSTATUS(), etc.
**Test:** Test with various exit codes

#### Issue 6: PATH Search Issues
**Problem:** execvp searches PATH, but what if PATH is empty/corrupted?
**Impact:** Might not find commands
**Solution:** execvp handles this, we just catch FileNotFoundError
**Test:** Test with non-existent command

#### Issue 7: Current Directory Changes
**Problem:** Built-in cd changes parent's directory, but fork preserves it for child
**Impact:** None - this is correct behavior
**Solution:** No action needed
**Test:** Test that child sees same directory as parent at fork time

#### Issue 8: Configuration Defaults
**Problem:** What if config is missing execution settings?
**Impact:** Could crash with KeyError
**Solution:** Use .get() with defaults everywhere
**Test:** Test with empty config dict

#### Issue 9: Output Buffering
**Problem:** stdout/stderr might be buffered, causing mixed output
**Impact:** Confusing output ordering
**Solution:** Let Python handle it (usually fine for interactive shell)
**Test:** Manual testing of output order

#### Issue 10: Very Long-Running Commands
**Problem:** waitpid blocks indefinitely
**Impact:** Shell appears frozen
**Solution:** This is correct behavior (bash does same)
**Test:** Test with `sleep 5` command

---

## 3. Approach Analysis

### Approach 1: Simple Sequential Implementation
**Implementation:**
```python
def execute_external_command(args, config):
    # 1. Fork
    pid = os.fork()
    
    if pid == 0:
        # 2. Child: reset signals, exec
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        try:
            os.execvp(args[0], args)
        except FileNotFoundError:
            print(f"{args[0]}: command not found", file=sys.stderr)
            sys.exit(127)
    else:
        # 3. Parent: wait, extract status
        pid, status = os.waitpid(pid, 0)
        display_exit_status(status, config)
        return extract_exit_code(status)
```

**Strengths:**
- Straightforward, easy to understand
- Follows specification exactly
- Clear separation of child/parent logic
- Matches technical specification structure
- Easy to test each section

**Weaknesses:**
- Doesn't handle fork failure
- Doesn't handle exec errors comprehensively
- Missing debug output
- No platform detection

**Verdict:** ✅ **BEST starting point** - Simple, correct, testable

---

### Approach 2: Defensive Programming with Error Checks
**Implementation:**
```python
def execute_external_command(args, config):
    # Validate inputs
    if not args or not args[0]:
        print("Error: No command specified", file=sys.stderr)
        return 1
    
    # Show debug info
    if config.get('debug', {}).get('show_fork_pids', False):
        print(f"[Forking to execute: {args[0]}]", file=sys.stderr)
    
    # Fork with error handling
    try:
        pid = os.fork()
    except OSError as e:
        print(f"Error: Fork failed: {e}", file=sys.stderr)
        return 1
    
    # Rest of implementation...
```

**Strengths:**
- Handles all error cases explicitly
- Provides debug information
- Input validation
- Defensive programming
- Production-ready code

**Weaknesses:**
- More complex than needed for assignment
- Parser already validates input
- Slightly harder to test (more code paths)

**Verdict:** ✅ **BEST for production** - Comprehensive, robust

---

### Approach 3: Platform-Aware with Subprocess Fallback
**Implementation:**
```python
def execute_external_command(args, config):
    if sys.platform == 'win32':
        # Windows: use subprocess as fallback
        return _execute_with_subprocess(args, config)
    else:
        # Linux/Unix: use fork/exec
        return _execute_with_fork(args, config)
```

**Strengths:**
- Cross-platform support
- Educational (shows both methods)
- More universally useful

**Weaknesses:**
- Assignment specifically requires fork/exec/wait
- Added complexity not required
- Would need to test both code paths
- Subprocess doesn't demonstrate process management

**Verdict:** ❌ **Out of scope** - Assignment requires POSIX syscalls

---

## 4. Selected Approach: Defensive Sequential (Hybrid of 1 & 2)

### Design Decisions

**Combine the best of Approach 1 and 2:**
- Simple, straightforward structure (Approach 1)
- Comprehensive error handling (Approach 2)
- Debug support (Approach 2)
- Input validation only where necessary (Approach 2)
- No platform detection (Linux-only as per requirements)

**Error Handling Strategy:**
- Fork failure: catch OSError, return 1
- Exec failure: child catches FileNotFoundError/PermissionError, exits with 127/126
- Wait failure: catch ChildProcessError (shouldn't happen), return 1
- All errors print to stderr

**Exit Code Convention (POSIX Standard):**
- 0-125: Command-specific exit codes
- 126: Command found but not executable (PermissionError)
- 127: Command not found (FileNotFoundError)
- 128+N: Command terminated by signal N

**Signal Handling:**
- Child resets SIGINT to default immediately after fork
- Parent's handler remains unchanged (will be set by shell loop)
- This allows Ctrl+C to kill child but not parent

**Configuration Integration:**
- Use .get() with defaults for all config access
- Support all debug and execution settings
- Never crash on missing config

---

## 5. Implementation Details

### 5.1 Function: execute_external_command()

```python
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
    if config.get('debug', {}).get('show_fork_pids', False):
        print(f"[About to fork for: {args[0]}]", file=sys.stderr)
    
    # Step 1: Fork the process
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
        # Reset signal handlers to default so child can be interrupted
        # Without this, Ctrl+C would kill the parent shell
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        
        # Try to replace process image with the command
        try:
            # execvp() searches PATH for the command and replaces this process
            # This call never returns on success (process is replaced)
            os.execvp(args[0], args)
        except FileNotFoundError:
            # Command not found in PATH
            # Use POSIX standard exit code 127
            print(f"{args[0]}: command not found", file=sys.stderr)
            sys.exit(127)
        except PermissionError:
            # Command found but not executable
            # Use POSIX standard exit code 126
            print(f"{args[0]}: Permission denied", file=sys.stderr)
            sys.exit(126)
        except Exception as e:
            # Catch any other unexpected errors
            # Use generic error code 1
            print(f"{args[0]}: {e}", file=sys.stderr)
            sys.exit(1)
    
    else:
        # PARENT PROCESS PATH
        # Debug output showing child PID
        if config.get('debug', {}).get('show_fork_pids', False):
            print(f"[Forked child PID: {pid}]", file=sys.stderr)
        
        # Step 3: Wait for child to complete
        try:
            # waitpid() blocks until the specific child exits
            # Returns tuple: (child_pid, status)
            # status is encoded and needs POSIX macros to extract info
            child_pid, status = os.waitpid(pid, 0)
        except ChildProcessError:
            # This shouldn't happen (child already reaped)
            # But handle it defensively
            print("Error: Child process not found", file=sys.stderr)
            return 1
        
        # Step 4: Display exit status if configured
        display_exit_status(status, config)
        
        # Step 5: Extract and return exit code
        if os.WIFEXITED(status):
            # Process exited normally - extract exit code
            return os.WEXITSTATUS(status)
        elif os.WIFSIGNALED(status):
            # Process was terminated by signal
            # Return 128 + signal number (common convention)
            return 128 + os.WTERMSIG(status)
        else:
            # Process was stopped or continued (shouldn't happen with default waitpid)
            # Return generic error code
            return 1
```

### 5.2 Function: display_exit_status()

```python
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
    show_mode = config.get('execution', {}).get('show_exit_codes', 'on_failure')
    format_str = config.get('execution', {}).get('exit_code_format', '[Exit: {code}]')
    
    # Check how the process terminated
    if os.WIFEXITED(status):
        # Process exited normally
        exit_code = os.WEXITSTATUS(status)
        
        # Determine if we should display based on mode
        should_display = False
        if show_mode == 'always':
            should_display = True
        elif show_mode == 'on_failure' and exit_code != 0:
            should_display = True
        elif show_mode == 'never':
            should_display = False
        
        # Display if configured
        if should_display:
            # Use format string from config
            # Handle format errors gracefully
            try:
                message = format_str.format(code=exit_code)
                print(message)
            except (KeyError, ValueError) as e:
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
```

---

## 6. Edge Cases to Handle

### 6.1 Fork Failure Cases

**Case:** System process limit reached
```python
# Test: Mock fork to raise OSError(errno.EAGAIN)
# Expected: Print error, return 1
```

**Case:** System out of memory
```python
# Test: Mock fork to raise OSError(errno.ENOMEM)
# Expected: Print error, return 1
```

### 6.2 Exec Failure Cases

**Case:** Command not in PATH
```python
# Test: execute_external_command(['nonexistent_command_xyz'], config)
# Expected: Print "command not found", return 127
```

**Case:** Command exists but not executable
```python
# Test: Create file without +x permission, try to execute
# Expected: Print "Permission denied", return 126
```

**Case:** Command is a directory
```python
# Test: execute_external_command(['/tmp'], config)
# Expected: Treated as PermissionError, return 126
```

### 6.3 Signal Cases

**Case:** Command terminates on SIGKILL
```python
# Test: Run command, kill from outside
# Expected: Display "Terminated by signal 9", return 137 (128+9)
```

**Case:** Command terminates on SIGTERM
```python
# Test: Run command, terminate gracefully
# Expected: Display "Terminated by signal 15", return 143 (128+15)
```

### 6.4 Configuration Cases

**Case:** Missing execution config
```python
# Test: execute_external_command(['ls'], {})
# Expected: Use defaults (on_failure mode)
```

**Case:** Invalid show_exit_codes value
```python
# Test: config = {'execution': {'show_exit_codes': 'invalid'}}
# Expected: Treat as 'never' or use default
```

**Case:** Invalid format string
```python
# Test: config = {'execution': {'exit_code_format': 'Bad {invalid}'}}
# Expected: Fall back to default format
```

### 6.5 Special Command Cases

**Case:** Empty args list
```python
# Test: execute_external_command([], config)
# Expected: Print error, return 1
```

**Case:** Command with no arguments
```python
# Test: execute_external_command(['ls'], config)
# Expected: Execute normally
```

**Case:** Command with many arguments (100+)
```python
# Test: execute_external_command(['echo'] + ['arg'] * 100, config)
# Expected: Execute normally (no arbitrary limit)
```

### 6.6 Exit Code Cases

**Case:** Command exits with 0
```python
# Test: execute_external_command(['true'], config)
# Expected: Return 0, display based on config
```

**Case:** Command exits with 1
```python
# Test: execute_external_command(['false'], config)
# Expected: Return 1, display if on_failure or always
```

**Case:** Command exits with custom code (e.g., 42)
```python
# Test: execute_external_command(['bash', '-c', 'exit 42'], config)
# Expected: Return 42
```

---

## 7. Test Plan

### 7.1 Test Structure

**Test File:** `tests/test_executor.py`

**Test Classes:**
1. **TestExecuteExternalCommandSuccess** (5+ tests)
   - Simple command (ls, pwd)
   - Command with arguments
   - Command with many arguments
   - Command exit code 0
   - Integration with config

2. **TestExecuteExternalCommandFailure** (5+ tests)
   - Command not found (return 127)
   - Permission denied (return 126)
   - Command exits with error code
   - Fork failure (mocked)
   - Empty args list

3. **TestExecuteExternalCommandSignals** (3+ tests)
   - Command terminated by SIGTERM
   - Command terminated by SIGKILL
   - Command terminated by SIGINT

4. **TestDisplayExitStatus** (8+ tests)
   - Mode: never (no output)
   - Mode: on_failure with success (no output)
   - Mode: on_failure with failure (show)
   - Mode: always with success (show)
   - Mode: always with failure (show)
   - Signal termination display
   - Invalid format string handling
   - Missing config

5. **TestExecuteExternalCommandConfig** (5+ tests)
   - show_fork_pids enabled
   - show_fork_pids disabled
   - Custom exit_code_format
   - Missing config (use defaults)
   - Partial config

6. **TestExecuteExternalCommandEdgeCases** (5+ tests)
   - Very long command lines
   - Commands with special characters
   - Commands that change directory (child only)
   - Commands that print to stderr
   - Commands that read from stdin

7. **TestExecuteExternalCommandIntegration** (5+ tests)
   - With parser output
   - Multiple sequential commands
   - Exit codes preserved across commands
   - Debug output verification
   - Realistic command sequences

**Target:** 35+ tests total
**Coverage Goal:** 95%+ (continuing the trend: 92% → 97% → 100% → 95%+)

### 7.2 Testing Challenges & Solutions

**Challenge 1: Testing fork/exec**
- **Problem:** Can't easily mock system calls
- **Solution:** Use unittest.mock.patch for fork, test with real commands

**Challenge 2: Testing signal handling**
- **Problem:** Hard to send signals during test
- **Solution:** Use subprocess to send signals, or test with commands that self-terminate

**Challenge 3: Testing exit codes**
- **Problem:** Need commands with specific exit codes
- **Solution:** Use `bash -c 'exit N'` to generate any exit code

**Challenge 4: Platform dependency**
- **Problem:** fork() only works on Linux/Unix
- **Solution:** Skip tests on Windows with @pytest.mark.skipif

**Challenge 5: Process cleanup**
- **Problem:** Failed tests might leave zombie processes
- **Solution:** Use fixtures with cleanup, ensure waitpid always called

### 7.3 Test Fixtures

```python
import pytest
import os
import tempfile
from unittest.mock import patch, MagicMock

@pytest.fixture
def default_config():
    """Provide default configuration for tests."""
    from akujobip1.config import get_default_config
    return get_default_config()

@pytest.fixture
def silent_config():
    """Config that never shows exit codes."""
    return {
        'execution': {
            'show_exit_codes': 'never',
            'exit_code_format': '[Exit: {code}]'
        },
        'debug': {
            'show_fork_pids': False
        }
    }

@pytest.fixture
def verbose_config():
    """Config that always shows everything."""
    return {
        'execution': {
            'show_exit_codes': 'always',
            'exit_code_format': '[Exit: {code}]'
        },
        'debug': {
            'show_fork_pids': True
        }
    }

@pytest.fixture
def mock_fork_failure():
    """Mock fork to simulate failure."""
    with patch('os.fork') as mock:
        mock.side_effect = OSError("Resource temporarily unavailable")
        yield mock
```

---

## 8. Potential Bugs & Preventions

### Bug 1: Forgetting to Wait
**Symptom:** Zombie processes accumulate
**Prevention:** Always call waitpid, even in error cases
**Test:** Check process table for zombies after tests

### Bug 2: Wrong Signal Handler Reset
**Symptom:** Ctrl+C kills parent shell
**Prevention:** Child resets to SIG_DFL immediately after fork
**Test:** Manual testing with Ctrl+C during command

### Bug 3: Incorrect Exit Code Extraction
**Symptom:** Wrong exit codes displayed
**Prevention:** Use WIFEXITED before WEXITSTATUS
**Test:** Test with various exit codes (0, 1, 42, 127, 126)

### Bug 4: Missing Error Message to stderr
**Symptom:** Errors go to stdout
**Prevention:** Always use `file=sys.stderr` for errors
**Test:** Check capsys.readouterr().err

### Bug 5: Format String Injection
**Symptom:** User config crashes format()
**Prevention:** Try/except around format_str.format()
**Test:** Test with invalid format strings

### Bug 6: Race Condition with Signals
**Symptom:** Intermittent signal handling issues
**Prevention:** Reset signal handler before exec
**Test:** Code review (hard to test reliably)

### Bug 7: PATH Not Searched
**Symptom:** Commands not found even though in PATH
**Prevention:** Use execvp (not execv)
**Test:** Test with command that's only in PATH

### Bug 8: Child Errors Kill Parent
**Symptom:** Shell crashes on exec failure
**Prevention:** Child must sys.exit() on error, not return
**Test:** Test with nonexistent command

### Bug 9: Status Encoding Confusion
**Symptom:** Wrong interpretation of waitpid status
**Prevention:** Use os.WIFEXITED, not manual bit manipulation
**Test:** Test with signals and various exit codes

### Bug 10: Configuration KeyError
**Symptom:** Crash when config keys missing
**Prevention:** Use .get() with defaults everywhere
**Test:** Test with empty config dict

---

## 9. Implementation Order

### Phase 1: Basic Structure (30 minutes)
1. Add imports (os, sys, signal, typing)
2. Create function signatures with docstrings
3. Add TODO comments for each section

### Phase 2: execute_external_command() - Fork/Exec/Wait (1 hour)
1. Implement input validation
2. Implement fork with error handling
3. Implement child path (signal reset, execvp, error handling)
4. Implement parent path (waitpid, status extraction)
5. Add debug output
6. Add comments explaining each step

### Phase 3: display_exit_status() (30 minutes)
1. Implement configuration access with defaults
2. Implement mode logic (never/on_failure/always)
3. Implement status checking (WIFEXITED, WIFSIGNALED, etc.)
4. Implement format string handling with fallback
5. Add edge case handling

### Phase 4: Testing - Success Cases (1 hour)
1. Write TestExecuteExternalCommandSuccess class
2. Test simple commands (ls, pwd, true, false)
3. Test with arguments
4. Test exit code returns
5. Run tests, fix any issues

### Phase 5: Testing - Failure Cases (1 hour)
1. Write TestExecuteExternalCommandFailure class
2. Test command not found (127)
3. Test permission denied (126)
4. Mock fork failure
5. Run tests, fix any issues

### Phase 6: Testing - Display Function (45 minutes)
1. Write TestDisplayExitStatus class
2. Test all three modes (never/on_failure/always)
3. Test format strings
4. Test signal termination
5. Run tests, fix any issues

### Phase 7: Testing - Integration & Edge Cases (1 hour)
1. Write remaining test classes
2. Test config integration
3. Test edge cases
4. Test with parser output
5. Run full test suite

### Phase 8: Coverage & Quality (30 minutes)
1. Run pytest with coverage
2. Identify untested lines
3. Add tests for missed coverage
4. Fix any linter errors
5. Verify 95%+ coverage

### Phase 9: Documentation (30 minutes)
1. Review all docstrings
2. Add examples to docstrings
3. Add inline comments
4. Update changelog
5. Update implementation checklist

**Total Estimated Time:** 6-7 hours

---

## 10. Success Criteria

- [ ] execute_external_command() fully implemented
- [ ] display_exit_status() fully implemented
- [ ] 35+ unit tests pass
- [ ] 95%+ code coverage achieved
- [ ] No linter errors
- [ ] All error cases handled gracefully
- [ ] Configuration integration working
- [ ] Signal handling correct
- [ ] Exit codes follow POSIX standards
- [ ] Documentation complete with examples
- [ ] Changelog updated
- [ ] Manual testing complete (ls, cd, nonexistent command, Ctrl+C)

---

## 11. Integration Checklist

### With Config System (Phase 2.1)
- [ ] Uses config['execution']['show_exit_codes']
- [ ] Uses config['execution']['exit_code_format']
- [ ] Uses config['debug']['show_fork_pids']
- [ ] Works with missing config (uses defaults)
- [ ] Works with partial config

### With Parser (Phase 2.2)
- [ ] Accepts List[str] from parser
- [ ] Handles args[0] as command name
- [ ] Works with any number of arguments
- [ ] No assumptions about parser internals

### With Built-ins (Phase 2.3)
- [ ] Never called for built-in commands (shell loop handles this)
- [ ] No functionality overlap
- [ ] Similar error handling patterns

### With Future Shell Loop (Phase 2.5)
- [ ] Returns int exit code
- [ ] Never raises exceptions
- [ ] Prints errors to stderr
- [ ] Handles empty args gracefully
- [ ] Ready to be called from main loop

---

## 12. Review Questions

Before implementation, verify:

1. **Is fork/exec/wait correct?**
   - Fork creates child ✓
   - Child execs command ✓
   - Parent waits for child ✓

2. **Are signals handled?**
   - Child resets SIGINT ✓
   - Parent's handler unchanged ✓

3. **Are errors handled?**
   - Fork failure ✓
   - Exec failure (not found, permission) ✓
   - Wait failure ✓

4. **Are exit codes correct?**
   - 127 for not found ✓
   - 126 for permission ✓
   - 128+N for signals ✓

5. **Is config integration safe?**
   - Uses .get() with defaults ✓
   - Never crashes on missing keys ✓

6. **Is testing comprehensive?**
   - 35+ tests planned ✓
   - 95%+ coverage target ✓
   - All edge cases covered ✓

---

## 13. Known Limitations

**Limitation 1: Linux/Unix Only**
- Fork is not available on Windows
- Solution: Document as Linux-only requirement
- Already stated in project requirements

**Limitation 2: No Job Control**
- Can't background processes (&)
- Can't bring to foreground (fg)
- Solution: Out of scope for this assignment

**Limitation 3: No Pipes**
- Can't pipe between commands (|)
- Solution: Out of scope (Phase 1 decision)

**Limitation 4: No Redirects**
- Can't redirect stdout/stderr (>, <, 2>)
- Solution: Out of scope (Phase 1 decision)

**Limitation 5: Single Command Only**
- Can't chain commands (&&, ||, ;)
- Solution: Out of scope for this assignment

---

## 14. Post-Implementation Tasks

After implementation complete:

1. **Update Changelog**
   - Add Phase 2.4 section
   - Document all functions implemented
   - List all tests written
   - Note coverage achieved

2. **Update Implementation Checklist**
   - Mark Phase 2.4 complete
   - Update progress tracking
   - Note any deviations from plan

3. **Update Version**
   - Increment to 0.5.0
   - Update in pyproject.toml
   - Update in __init__.py

4. **Code Review**
   - Self-review for issues
   - Check all error paths
   - Verify signal handling
   - Test manually with various commands

5. **Documentation**
   - Ensure all docstrings complete
   - Verify examples work
   - Check inline comments
   - Update any diagrams if needed

---

**Plan Status:** READY FOR IMPLEMENTATION  
**Next Step:** Begin Phase 1 - Basic Structure

**Estimated Completion:** Phase 2.4 complete within 6-7 hours of focused work

