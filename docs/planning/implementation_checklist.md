# AkujobiP1Shell - Implementation Checklist

**Project:** CSC456 Programming Assignment 1
**Author:** John Akujobi
**Date:** 2025-11-09

---

## Phase 1: Project Setup and Core Structure

### 1.1 Directory Structure
- [ ] Create `src/akujobip1/` directory
- [ ] Create `src/akujobip1/__init__.py`
- [ ] Create `src/akujobip1/shell.py` (main shell logic)
- [ ] Create `src/akujobip1/config.py` (configuration management)
- [ ] Create `src/akujobip1/builtins.py` (built-in commands)
- [ ] Create `src/akujobip1/executor.py` (process execution)
- [ ] Create `src/akujobip1/parser.py` (command parsing)

### 1.2 Configuration Files
- [ ] Create default `akujobip1.yaml` configuration file
- [ ] Create example configuration in `examples/config.yaml`
- [ ] Update `.gitignore` for Python artifacts

### 1.3 Dependencies
- [ ] Verify `pyproject.toml` dependencies
- [ ] Generate `requirements.txt` from pyproject.toml
- [ ] Test `pip install -e .` installation

---

## Phase 2: Core Shell Implementation

### 2.1 Configuration System (config.py)
- [ ] Implement `load_config()` function
  - [ ] Check `$AKUJOBIP1_CONFIG` environment variable
  - [ ] Check `./akujobip1.yaml` (current directory)
  - [ ] Check `~/.config/akujobip1/config.yaml` (user config)
  - [ ] Fallback to built-in defaults
- [ ] Implement `merge_config()` for deep merging
- [ ] Implement `validate_config()` for validation
- [ ] Implement `expand_paths()` for tilde expansion
- [ ] Add configuration schema documentation
- [ ] Write unit tests for config loading

### 2.2 Command Parser (parser.py)
- [ ] Implement `parse_command(command_line)` function
  - [ ] Use `shlex.split()` for tokenization
  - [ ] Handle quoted arguments correctly
  - [ ] Handle empty input
  - [ ] Handle whitespace-only input
- [ ] Implement `expand_wildcards(args)` function
  - [ ] Use `glob.glob()` for wildcard expansion
  - [ ] Handle no matches (return literal)
  - [ ] Handle multiple wildcards
- [ ] Write unit tests for parser
  - [ ] Test quoted arguments
  - [ ] Test wildcards
  - [ ] Test edge cases

### 2.3 Built-in Commands (builtins.py)
- [ ] Create `BuiltinCommand` base class
- [ ] Implement `exit` command
  - [ ] Print configured exit message
  - [ ] Return exit code to shell
- [ ] Implement `cd` command
  - [ ] Handle no arguments (cd to home)
  - [ ] Handle directory path argument
  - [ ] Handle `cd -` (previous directory)
  - [ ] Error handling for invalid paths
  - [ ] Optionally show pwd after cd (if configured)
- [ ] Implement `pwd` command
  - [ ] Print current working directory
- [ ] Implement `help` command
  - [ ] List available built-in commands
  - [ ] Show usage information
- [ ] Create `get_builtin(name)` dispatcher function
- [ ] Write unit tests for each built-in

### 2.4 Process Executor (executor.py)
- [ ] Implement `execute_external_command(args, config)` function
  - [ ] Call `os.fork()` with error handling
  - [ ] Child process:
    - [ ] Reset signal handlers to default
    - [ ] Call `os.execvp(args[0], args)`
    - [ ] Handle `FileNotFoundError` (command not found)
    - [ ] Handle `PermissionError` (not executable)
    - [ ] Exit with appropriate code (127, 126)
  - [ ] Parent process:
    - [ ] Call `os.waitpid(pid, 0)`
    - [ ] Extract exit status
    - [ ] Display exit code if configured
    - [ ] Handle signals (WIFSIGNALED)
- [ ] Write unit tests for executor
  - [ ] Test successful execution
  - [ ] Test command not found
  - [ ] Test permission denied
  - [ ] Test exit code handling

### 2.5 Main Shell Loop (shell.py)
- [ ] Implement `cli()` function (entry point)
  - [ ] Load configuration
  - [ ] Set up signal handlers
  - [ ] Enter main loop
- [ ] Implement main REPL loop
  - [ ] Display prompt
  - [ ] Read input with `input()`
  - [ ] Handle EOFError (Ctrl+D)
  - [ ] Parse command
  - [ ] Check if built-in or external
  - [ ] Execute command
  - [ ] Continue loop
- [ ] Implement signal handlers
  - [ ] SIGINT handler (Ctrl+C)
    - [ ] Print newline
    - [ ] Show new prompt
    - [ ] Don't exit shell
  - [ ] Ensure child processes can be interrupted
- [ ] Write integration tests for main loop

---

## Phase 3: Error Handling and Edge Cases

### 3.1 Error Messages
- [ ] Implement standardized error format
- [ ] Add error messages to stderr (not stdout)
- [ ] Implement verbose error mode (configurable)
- [ ] Handle and display:
  - [ ] Command not found (exit 127)
  - [ ] Permission denied (exit 126)
  - [ ] Fork failure
  - [ ] Invalid arguments to built-ins
  - [ ] Configuration file errors

### 3.2 Edge Cases
- [ ] Handle empty input (show prompt again)
- [ ] Handle whitespace-only input
- [ ] Handle very long commands (1000+ chars)
- [ ] Handle commands with no PATH (absolute paths)
- [ ] Handle wildcards with no matches
- [ ] Handle Ctrl+C during command execution
- [ ] Handle Ctrl+D (EOF)
- [ ] Handle rapid command execution

---

## Phase 4: Testing

### 4.1 Unit Tests (pytest)
- [ ] `tests/test_config.py`
  - [ ] Test config loading from different locations
  - [ ] Test config merging
  - [ ] Test config validation
  - [ ] Test invalid YAML handling
  - [ ] Test missing config files (use defaults)

- [ ] `tests/test_parser.py`
  - [ ] Test simple command parsing
  - [ ] Test quoted arguments
  - [ ] Test multiple arguments
  - [ ] Test wildcard expansion
  - [ ] Test empty input
  - [ ] Test whitespace handling

- [ ] `tests/test_builtins.py`
  - [ ] Test `exit` command
  - [ ] Test `cd` command (various cases)
  - [ ] Test `pwd` command
  - [ ] Test `help` command
  - [ ] Test invalid built-in arguments

- [ ] `tests/test_executor.py`
  - [ ] Test successful command execution
  - [ ] Test command not found
  - [ ] Test permission denied
  - [ ] Test exit code handling
  - [ ] Test signal handling
  - [ ] Mock fork/exec/wait for testing

- [ ] `tests/test_shell.py`
  - [ ] Test main loop initialization
  - [ ] Test prompt display
  - [ ] Test command dispatch (built-in vs external)
  - [ ] Test signal handling
  - [ ] Test EOF handling
  - [ ] Integration tests

### 4.2 Bash Tests
- [ ] Verify existing tests in `tests/run_tests.sh`
- [ ] Update test expectations if needed
- [ ] Ensure all 4 tests pass:
  - [ ] Exit command test
  - [ ] Empty input then exit
  - [ ] Unknown command handling
  - [ ] Quoted arguments support

### 4.3 Code Coverage
- [ ] Install pytest-cov
- [ ] Run coverage analysis
- [ ] Achieve 90%+ coverage
- [ ] Generate HTML coverage report
- [ ] Identify and test uncovered code paths

### 4.4 Manual Testing
- [ ] Test on Ubuntu Linux
- [ ] Test various commands (ls, cp, mkdir, etc.)
- [ ] Test error conditions
- [ ] Test configuration variations
- [ ] Test signal handling interactively
- [ ] Performance test (run 100+ commands)

---

## Phase 5: CI/CD Pipeline

### 5.1 GitHub Actions Workflow
- [ ] Update `.github/workflows/ci.yml`
- [ ] Configure Python 3.10 setup
- [ ] Add dependency installation step
- [ ] Add pytest execution step
- [ ] Add bash test execution step
- [ ] Add code coverage reporting
- [ ] Add linting step (ruff)
- [ ] Add formatting check (black)

### 5.2 Code Quality
- [ ] Run `ruff check src/` and fix issues
- [ ] Run `black src/` to format code
- [ ] Verify no linting warnings
- [ ] Ensure consistent code style

---

## Phase 6: Documentation

### 6.1 Architecture Diagrams
- [ ] Create component architecture diagram
  - [ ] Shell loop
  - [ ] Parser
  - [ ] Built-in dispatcher
  - [ ] External executor
  - [ ] Configuration system
- [ ] Create data flow diagram
- [ ] Create system call flow diagram (fork/exec/wait)
- [ ] Export diagrams as PNG/SVG

### 6.2 Code Documentation
- [ ] Add Google-style docstrings to all functions
- [ ] Add detailed inline comments
- [ ] Document all edge cases
- [ ] Add POSIX standard references
- [ ] Ensure no emojis in code/comments

### 6.3 Report (`docs/report.md`)
- [ ] Write Introduction section
- [ ] Write Architecture section
  - [ ] Include architecture diagram
  - [ ] Explain component interactions
- [ ] Write System Call Flow section
  - [ ] Include sequence diagram
  - [ ] Explain fork/exec/wait process
- [ ] Write Code Walkthrough section
  - [ ] Main loop explanation
  - [ ] Parser explanation
  - [ ] Built-in commands explanation
  - [ ] External execution explanation
  - [ ] Error handling explanation
  - [ ] Configuration system explanation
- [ ] Add Screenshots section
  - [ ] Shell startup
  - [ ] Simple commands
  - [ ] Multi-argument commands
  - [ ] Built-in commands
  - [ ] Error handling
  - [ ] Exit command
  - [ ] Ctrl+C handling
  - [ ] Wildcard expansion
  - [ ] Configuration loading
  - [ ] Test execution
- [ ] Write How to Run section
- [ ] Write Testing section
- [ ] Write Conclusion
- [ ] Convert to PDF for submission

### 6.4 README
- [ ] Write project description
- [ ] Add features list
- [ ] Add requirements section
- [ ] Write installation instructions
- [ ] Write usage instructions
- [ ] Add configuration documentation
- [ ] List built-in commands
- [ ] Add testing instructions
- [ ] Add development instructions
- [ ] Add project structure section
- [ ] Add author information

### 6.5 Additional Documentation
- [ ] Update `docs/changelog.md` with version 1.0.0
- [ ] Create `examples/` directory with usage examples
- [ ] Create `examples/sample_session.txt` with example usage

---

## Phase 7: Final Polish

### 7.1 Code Review
- [ ] Review all source files for clarity
- [ ] Ensure consistent naming conventions
- [ ] Remove debug print statements
- [ ] Remove commented-out code
- [ ] Verify no hardcoded paths
- [ ] Check for proper exception handling

### 7.2 Testing Verification
- [ ] Run full test suite locally
- [ ] Verify all tests pass
- [ ] Check code coverage report
- [ ] Run bash tests
- [ ] Verify CI pipeline passes

### 7.3 Documentation Review
- [ ] Proofread report for typos
- [ ] Verify all diagrams are clear
- [ ] Check all screenshots are legible
- [ ] Ensure README is complete
- [ ] Verify code comments are clear

---

## Phase 8: Submission Preparation

### 8.1 Git Repository
- [ ] Commit all changes with clear messages
- [ ] Push to remote repository
- [ ] Verify branch: `claude/simple-shell-implementation-011CUwcRWXvEbNaNidFTJ9NZ`
- [ ] Tag release: `v1.0.0`
- [ ] Push tags to remote

### 8.2 Create Submission Zip
- [ ] Create clean directory structure
- [ ] Copy source files
- [ ] Copy test files
- [ ] Copy documentation (including PDF report)
- [ ] Copy configuration files
- [ ] Copy pyproject.toml
- [ ] Generate requirements.txt
- [ ] Include README.md
- [ ] Create zip: `CSC456_ProAssgn1_Akujobi.zip`
- [ ] Verify zip contents
- [ ] Test zip on clean system

### 8.3 GitHub Release
- [ ] Create GitHub release for v1.0.0
- [ ] Write release description
- [ ] Attach submission zip file
- [ ] Publish release

### 8.4 Final Verification
- [ ] Test on fresh Ubuntu VM/container
- [ ] Clone repository
- [ ] Install with `pip install -e .`
- [ ] Run shell and test commands
- [ ] Run test suite
- [ ] Verify everything works

---

## Evaluation Self-Check

### Documentation (20%)
- [ ] Report includes all required sections
- [ ] Architecture diagrams present and clear
- [ ] System call flow explained
- [ ] Code walkthrough is detailed
- [ ] Screenshots show all features
- [ ] README is comprehensive
- [ ] Code is well-commented

### Compilation (15%)
- [ ] `pip install -e .` works without errors
- [ ] No warnings during installation
- [ ] Shell runs with `akujobip1` command
- [ ] Shell runs with `python -m akujobip1`

### Correctness (60%)
- [ ] Prompt displays correctly: `AkujobiP1> `
- [ ] Commands execute with arguments
- [ ] `exit` command works with "Bye!" message
- [ ] Parent waits for child completion
- [ ] Commands with 1 argument work
- [ ] Commands with 2 arguments work
- [ ] Commands with 3 arguments work
- [ ] Error handling works (command not found)
- [ ] All bash tests pass
- [ ] All pytest tests pass

### Readability & Misc (5%)
- [ ] Code is well-formatted (black)
- [ ] Code is well-commented
- [ ] Zip file name correct: `CSC456_ProAssgn1_Akujobi.zip`
- [ ] Zip contains all necessary files
- [ ] No unnecessary files in zip

---

## Progress Tracking

**Current Status:** Planning Complete - Ready for Implementation

**Next Steps:**
1. Create source directory structure
2. Implement configuration system
3. Implement command parser
4. Implement built-in commands
5. Implement process executor
6. Implement main shell loop

**Estimated Completion Time:** 3-4 weeks
- Week 1: Core implementation
- Week 2: Testing and debugging
- Week 3: Documentation
- Week 4: Final polish and submission

---

## Notes

**Key Success Factors:**
- Focus on correctness first (60% of grade)
- Comprehensive documentation (20% of grade)
- Clean, commented code (5% of grade)
- Proper submission format

**Common Pitfalls to Avoid:**
- Forgetting to wait for child process
- Not handling command not found errors
- Incorrect exit status handling
- Poor error messages
- Incomplete documentation
- Missing test coverage

**Resources:**
- POSIX fork: https://man7.org/linux/man-pages/man2/fork.2.html
- POSIX exec: https://man7.org/linux/man-pages/man3/exec.3.html
- POSIX wait: https://man7.org/linux/man-pages/man2/wait.2.html
- Python os module: https://docs.python.org/3/library/os.html
- shlex module: https://docs.python.org/3/library/shlex.html

---

**Checklist Version:** 1.0
**Last Updated:** 2025-11-09
**Status:** Ready for Implementation
