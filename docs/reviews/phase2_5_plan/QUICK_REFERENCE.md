# Phase 2.5 Quick Reference Card

**Date:** 2025-11-10  
**Phase:** Main Shell Loop (shell.py)  
**Status:** Planning Complete

---

## Implementation at a Glance

### What We're Building

Main REPL loop that integrates all existing modules:
```
User Input → Parser → Built-in Check → Execute → Loop
                ↓           ↓
            Config      Executor
```

### Files to Modify

- `src/akujobip1/shell.py` - Main implementation
- `tests/test_shell.py` - Test suite (50 tests)

### Key Functions

```python
def cli() -> int:
    """Entry point - loads config and runs shell"""
    
def run_shell(config: Dict[str, Any]) -> int:
    """Main REPL loop"""
```

---

## Critical Implementation Details

### 1. NO CUSTOM SIGNAL HANDLERS

**Use Python's default behavior:**
```python
# CORRECT - Simple and safe
try:
    line = input(prompt)
except KeyboardInterrupt:
    print()
    continue
except EOFError:
    print()
    print(exit_message)
    return 0
```

**Why no custom handlers?**
- Python default works correctly
- Custom handlers would interfere with executor
- Executor already resets signals in child
- Simpler = fewer bugs

### 2. CHECK FOR EXIT CODE -1

**Exit command returns -1, not 0:**
```python
# CRITICAL - Check for -1
exit_code = builtin.execute(args, config)
if exit_code == -1:
    return 0  # Shell exits successfully
```

**Why -1?**
- 0 means "success, continue shell"
- -1 means "terminate shell now"
- Allows exit to print message first

### 3. HANDLE EMPTY ARGS

**Parser returns [] for empty/invalid input:**
```python
# CRITICAL - Check before indexing
args = parse_command(command_line, config)
if not args:
    continue  # Skip empty input
builtin = get_builtin(args[0])  # Safe now
```

### 4. USE .get() FOR CONFIG

**Config keys might be missing:**
```python
# CORRECT - Safe with defaults
prompt = config.get('prompt', {}).get('text', 'AkujobiP1> ')
exit_msg = config.get('exit', {}).get('message', 'Bye!')
```

---

## Main Loop Algorithm

```python
while True:
    try:
        # 1. Read input
        command_line = input(prompt)
        
        # 2. Parse
        args = parse_command(command_line, config)
        
        # 3. Skip empty
        if not args:
            continue
        
        # 4. Check built-in
        builtin = get_builtin(args[0])
        
        if builtin:
            # 5a. Execute built-in
            exit_code = builtin.execute(args, config)
            if exit_code == -1:  # Exit signal
                return 0
        else:
            # 5b. Execute external
            execute_external_command(args, config)
        
    except EOFError:
        # Ctrl+D - exit gracefully
        print()
        print(config.get('exit', {}).get('message', 'Bye!'))
        return 0
        
    except KeyboardInterrupt:
        # Ctrl+C - show new prompt
        print()
        continue
```

---

## Module Interfaces

### Configuration (Phase 2.1)
```python
from akujobip1.config import load_config
config = load_config()  # Dict[str, Any]
```

### Parser (Phase 2.2)
```python
from akujobip1.parser import parse_command
args = parse_command(line, config)  # List[str]
# Returns [] for empty/invalid
```

### Builtins (Phase 2.3)
```python
from akujobip1.builtins import get_builtin
builtin = get_builtin('exit')  # BuiltinCommand | None
code = builtin.execute(args, config)  # int (-1 = exit)
```

### Executor (Phase 2.4)
```python
from akujobip1.executor import execute_external_command
code = execute_external_command(args, config)  # int (0-255)
```

---

## Signal Handling

### Ctrl+C Behavior

**During input:**
```
User presses Ctrl+C
    ↓
Python raises KeyboardInterrupt
    ↓
Shell catches exception
    ↓
Print newline, show new prompt
```

**During command:**
```
User presses Ctrl+C
    ↓
Signal goes to child process
    ↓
Child terminates (executor handles)
    ↓
Parent returns from waitpid()
    ↓
Shell continues to next prompt
```

### Ctrl+D Behavior

```
User presses Ctrl+D
    ↓
Python raises EOFError
    ↓
Shell catches exception
    ↓
Print exit message
    ↓
Return 0 (exit gracefully)
```

---

## Bash Tests

### Test 1: Exit
```bash
Input:  "exit"
Output: "AkujobiP1> Bye!\n"
```

### Test 2: Empty Then Exit
```bash
Input:  "\nexit"
Output: "AkujobiP1> AkujobiP1> Bye!\n"
```

### Test 3: Unknown Command
```bash
Input:  "defnotcmd\nexit\n"
Output: Contains "defnotcmd: command not found"
```

### Test 4: Quoted Args
```bash
Input:  'printf "%s %s\n" "a b" c\nexit\n'
Output: Command executes successfully
```

---

## Test Plan

### Test Classes (50 tests)

1. **TestBasicFunctionality** (8 tests)
   - Prompt display
   - Empty input handling
   - Command execution
   - Exit behavior

2. **TestBuiltinIntegration** (8 tests)
   - exit, cd, pwd, help
   - Error handling
   - Return value checks

3. **TestExternalCommandIntegration** (8 tests)
   - Command execution
   - Error handling
   - Exit codes

4. **TestSignalHandling** (6 tests)
   - Ctrl+C during input
   - Ctrl+C during command
   - Ctrl+D handling
   - Multiple signals

5. **TestErrorHandling** (5 tests)
   - Parse errors
   - Built-in errors
   - Executor errors
   - Unexpected errors

6. **TestEdgeCases** (5 tests)
   - Very long input
   - Multiple commands
   - Whitespace handling
   - Special characters

7. **TestConfigurationIntegration** (5 tests)
   - Custom prompt
   - Custom exit message
   - Missing config keys
   - Invalid config

8. **TestBashTestSimulation** (5 tests)
   - Simulate all 4 bash tests
   - Verify output matches

---

## Common Pitfalls

### ❌ WRONG: Custom Signal Handler
```python
def sigint_handler(signum, frame):
    print()
signal.signal(signal.SIGINT, sigint_handler)
```
**Problem:** Interferes with child signals

### ✅ CORRECT: Catch Exception
```python
try:
    line = input(prompt)
except KeyboardInterrupt:
    print()
    continue
```

---

### ❌ WRONG: Don't Check Exit Code
```python
builtin.execute(args, config)
# Shell never exits!
```

### ✅ CORRECT: Check for -1
```python
exit_code = builtin.execute(args, config)
if exit_code == -1:
    return 0
```

---

### ❌ WRONG: Assume Args Not Empty
```python
args = parse_command(line, config)
builtin = get_builtin(args[0])  # IndexError!
```

### ✅ CORRECT: Check First
```python
args = parse_command(line, config)
if not args:
    continue
builtin = get_builtin(args[0])
```

---

### ❌ WRONG: Assume Config Keys Exist
```python
prompt = config['prompt']['text']  # KeyError!
```

### ✅ CORRECT: Use .get()
```python
prompt = config.get('prompt', {}).get('text', 'AkujobiP1> ')
```

---

## Success Criteria

- [ ] All 50 pytest tests pass
- [ ] All 4 bash tests pass
- [ ] Coverage >= 95%
- [ ] Zero linter errors
- [ ] Code < 200 lines
- [ ] Grade target: A+ (98/100)

---

## Implementation Checklist

### Phase 1: Core Implementation (1 hour)
- [ ] Update imports
- [ ] Implement cli()
- [ ] Implement run_shell()
- [ ] Add documentation

### Phase 2: Testing (2 hours)
- [ ] Write 50 tests
- [ ] Run pytest
- [ ] Achieve 95%+ coverage
- [ ] Run bash tests

### Phase 3: Quality (30 minutes)
- [ ] Lint with ruff
- [ ] Format with black
- [ ] Update changelog
- [ ] Final review

**Total Time: 3-4 hours**

---

## Key Metrics

| Metric | Target | Expected |
|--------|--------|----------|
| Test Count | 40+ | 50 |
| Coverage | 95%+ | 98% |
| Code Length | <200 lines | ~150 lines |
| Bash Tests | 4/4 pass | 4/4 pass |
| Linter Errors | 0 | 0 |
| Grade | A+ | A+ (98/100) |

---

## Integration Status

| Module | Status | Tests | Coverage |
|--------|--------|-------|----------|
| Config (2.1) | ✅ Ready | 39 | 92% |
| Parser (2.2) | ✅ Ready | 56 | 97% |
| Builtins (2.3) | ✅ Ready | 35 | 100% |
| Executor (2.4) | ✅ Ready | 41 | 80% (~95%) |
| **Shell (2.5)** | **📋 Planning** | **50 (planned)** | **95% (target)** |

**Total Existing Tests: 171 passing**

---

## Risk Assessment

| Risk | Likelihood | Impact | Status |
|------|-----------|--------|--------|
| Signal handling breaks | Low | High | ✅ Mitigated (no custom handler) |
| Exit doesn't work | Low | High | ✅ Mitigated (explicit check) |
| Empty args crash | Low | Medium | ✅ Mitigated (check before index) |
| Config missing keys | Low | Medium | ✅ Mitigated (use .get()) |
| Bash tests fail | Medium | High | 🔄 Will simulate in pytest first |

---

## Questions Before Starting?

**Q: Why no custom signal handler?**  
A: Python's default behavior is correct. Custom handlers would complicate things and could break child process handling.

**Q: How does Ctrl+C work during command execution?**  
A: Signal goes to child process (foreground). Executor handles it. Parent is blocked in waitpid() and not affected.

**Q: What if parser returns empty list?**  
A: Check with `if not args: continue` before using args[0].

**Q: What if exit command is called?**  
A: Returns -1. Check with `if exit_code == -1: return 0`.

**Q: How to test signal handling?**  
A: Mock input() to raise KeyboardInterrupt or EOFError.

---

**Ready to implement? YES ✅**

**Expected time:** 3-4 hours  
**Expected grade:** A+ (98/100)  
**Risk level:** LOW  
**Complexity:** MEDIUM

**Go build it!**

