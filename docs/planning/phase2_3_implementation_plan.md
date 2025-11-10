# Phase 2.3: Built-in Commands Implementation Plan

**Date:** 2025-11-10  
**Author:** John Akujobi  
**Status:** Planning

---

## 1. Requirements Analysis

### Exit Command
- Print configured exit message from `config['exit']['message']`
- Return special exit code that signals shell to terminate
- Should always work (no error conditions)

### CD Command
- `cd` (no args) - Change to home directory
- `cd <path>` - Change to specified directory (relative or absolute)
- `cd -` - Change to previous directory (OLDPWD)
- Handle errors: directory not found, permission denied
- Optionally show pwd after cd if `config['builtins']['cd']['show_pwd_after']`
- Track previous directory for `cd -` support

### PWD Command
- Print current working directory
- Use `os.getcwd()`
- Should always work (no error conditions in normal use)

### Help Command
- List all available built-in commands
- Show brief usage information for each
- Format output clearly

---

## 2. Approach Analysis

### Approach 1: Simple Function-Based Commands
**Implementation:**
- Each command is a simple method that directly implements functionality
- Use instance variables for state (like previous directory for cd)
- Minimal abstraction

**Strengths:**
- Simple and straightforward
- Easy to understand and test
- No over-engineering
- Direct access to all needed functionality

**Weaknesses:**
- Less flexible if we need to add command metadata later
- Each command instance needs to maintain state individually

**Verdict:** ✅ **BEST for this project** - Meets requirements, simple, testable

---

### Approach 2: Command Class Hierarchy with Metadata
**Implementation:**
- Add metadata to base class (name, description, usage)
- Commands override metadata methods
- Help command uses metadata from all commands

**Strengths:**
- Self-documenting commands
- Help command automatically stays updated
- More maintainable long-term

**Weaknesses:**
- More complex than needed
- Overkill for 4 commands
- Harder to test

**Verdict:** ❌ Too complex for current needs

---

### Approach 3: Shared State Manager
**Implementation:**
- Create a CommandState class to track shell state
- All commands share this state
- State includes OLDPWD, current config, etc.

**Strengths:**
- Clean separation of state and logic
- Easier to test state management
- More scalable

**Weaknesses:**
- Adds complexity
- Requires passing state around
- Not needed for current scope

**Verdict:** ❌ Over-engineered

---

## 3. Selected Approach: Simple Function-Based (Approach 1)

### Design Decisions

**State Management:**
- Use class variable `_previous_directory` for cd - command
- Shared across all CdCommand instances
- Simple and effective

**Error Handling:**
- Return non-zero exit codes on error
- Print error messages to stderr
- Never crash - always return gracefully

**Configuration Integration:**
- Accept config dict in execute() method
- Check config['builtins'][command]['enabled'] if needed
- Use config values for messages and behavior

**Exit Code Convention:**
- 0 = success
- 1 = general error
- 2 = misuse of command (wrong arguments)
- -1 = special code for exit command (signal to shell)

---

## 4. Implementation Details

### ExitCommand

```python
class ExitCommand(BuiltinCommand):
    """Exit the shell."""
    
    def execute(self, args: List[str], config: Dict[str, Any]) -> int:
        # Print exit message from config
        message = config.get('exit', {}).get('message', 'Bye!')
        print(message)
        
        # Return -1 to signal shell to exit
        return -1
```

**Tests:**
- Test with default message
- Test with custom message from config
- Test return code is -1

---

### CdCommand

```python
class CdCommand(BuiltinCommand):
    """Change directory."""
    
    # Class variable to track previous directory
    _previous_directory: Optional[str] = None
    
    def execute(self, args: List[str], config: Dict[str, Any]) -> int:
        # Determine target directory
        if len(args) == 1:  # Just "cd"
            target = os.path.expanduser('~')
        elif args[1] == '-':  # cd -
            if self._previous_directory is None:
                print("cd: OLDPWD not set", file=sys.stderr)
                return 1
            target = self._previous_directory
        else:  # cd <path>
            target = args[1]
        
        # Save current directory before changing
        try:
            current = os.getcwd()
        except OSError:
            current = None
        
        # Try to change directory
        try:
            os.chdir(target)
        except FileNotFoundError:
            print(f"cd: {target}: No such file or directory", file=sys.stderr)
            return 1
        except NotADirectoryError:
            print(f"cd: {target}: Not a directory", file=sys.stderr)
            return 1
        except PermissionError:
            print(f"cd: {target}: Permission denied", file=sys.stderr)
            return 1
        
        # Update previous directory
        if current:
            CdCommand._previous_directory = current
        
        # Optionally show pwd after cd
        if config.get('builtins', {}).get('cd', {}).get('show_pwd_after', False):
            print(os.getcwd())
        
        return 0
```

**Tests:**
- cd with no arguments (home)
- cd to valid directory
- cd to absolute path
- cd to relative path
- cd - with OLDPWD set
- cd - without OLDPWD set
- cd to non-existent directory
- cd to file (not directory)
- cd to directory without permissions
- show_pwd_after configuration
- Too many arguments

---

### PwdCommand

```python
class PwdCommand(BuiltinCommand):
    """Print working directory."""
    
    def execute(self, args: List[str], config: Dict[str, Any]) -> int:
        try:
            print(os.getcwd())
            return 0
        except OSError as e:
            print(f"pwd: {e}", file=sys.stderr)
            return 1
```

**Tests:**
- Print current directory
- Handle deleted directory edge case

---

### HelpCommand

```python
class HelpCommand(BuiltinCommand):
    """Show help information."""
    
    def execute(self, args: List[str], config: Dict[str, Any]) -> int:
        print("Built-in commands:")
        print("  exit       Exit the shell")
        print("  cd [dir]   Change directory (cd - for previous, cd for home)")
        print("  pwd        Print working directory")
        print("  help       Show this help message")
        return 0
```

**Tests:**
- Test output contains all commands
- Test return code is 0

---

## 5. Test Plan

### Test File: tests/test_builtins.py

**Test Classes:**
1. `TestExitCommand` (3 tests)
   - Default message
   - Custom message
   - Return code

2. `TestCdCommand` (12+ tests)
   - cd to home
   - cd to valid path
   - cd to absolute path
   - cd to relative path
   - cd - with OLDPWD
   - cd - without OLDPWD
   - cd to non-existent
   - cd to file
   - cd with permissions error
   - show_pwd_after enabled
   - show_pwd_after disabled
   - Multiple cd operations

3. `TestPwdCommand` (2 tests)
   - Print directory
   - Handle errors

4. `TestHelpCommand` (2 tests)
   - Output format
   - Return code

5. `TestGetBuiltin` (3 tests)
   - Get existing builtin
   - Get non-existent builtin
   - Verify all commands in registry

**Target Coverage:** 90%+ (aiming for 95%+)

---

## 6. Integration Points

**With Configuration System:**
- exit.message - Exit message text
- builtins.cd.enabled - Enable/disable cd
- builtins.cd.show_pwd_after - Show pwd after cd
- builtins.pwd.enabled - Enable/disable pwd
- builtins.help.enabled - Enable/disable help

**With Shell Loop (Future):**
- Shell checks return code == -1 to exit
- Shell calls get_builtin(name) to check if command is builtin
- Shell calls builtin.execute(args, config)

**With Parser (Current):**
- args[0] is command name
- args[1:] are arguments
- Parser already provides clean argument list

---

## 7. Edge Cases to Handle

**Exit Command:**
- None - always works

**CD Command:**
- Current directory deleted (getcwd fails)
- OLDPWD not set on first cd -
- cd with too many arguments (accept first, ignore rest)
- cd to ~ (expand home)
- cd to paths with spaces (parser handles)

**PWD Command:**
- Current directory deleted (getcwd fails)

**Help Command:**
- None - always works

---

## 8. Error Message Format

Following standard shell conventions:

```
command: error_details
```

Examples:
```
cd: /nonexistent: No such file or directory
cd: file.txt: Not a directory
cd: /root: Permission denied
cd: OLDPWD not set
```

---

## 9. Implementation Order

1. ExitCommand (simplest)
2. PwdCommand (simple)
3. HelpCommand (simple)
4. CdCommand (most complex)
5. Write tests for each after implementation
6. Run tests and fix issues
7. Check coverage
8. Update documentation

---

## 10. Success Criteria

- [ ] All 4 commands implemented
- [ ] 20+ unit tests pass
- [ ] 90%+ code coverage
- [ ] No linter errors
- [ ] All error cases handled gracefully
- [ ] Configuration integration working
- [ ] Documentation updated
- [ ] Changelog updated

---

**Plan Status:** READY FOR IMPLEMENTATION
**Next Step:** Implement ExitCommand

