# AkujobiP1Shell - Implementation Checklist

**Project:** CSC456 Programming Assignment 1
**Author:** John Akujobi
**Date:** 2025-11-09

---

## Phase 1: Project Setup and Core Structure

### 1.1 Directory Structure
- [x] Create `src/akujobip1/` directory
- [x] Create `src/akujobip1/__init__.py`
- [x] Create `src/akujobip1/shell.py` (main shell logic)
- [x] Create `src/akujobip1/config.py` (configuration management)
- [x] Create `src/akujobip1/builtins.py` (built-in commands)
- [x] Create `src/akujobip1/executor.py` (process execution)
- [x] Create `src/akujobip1/parser.py` (command parsing)

### 1.2 Configuration Files
- [x] Create default `akujobip1.yaml` configuration file
- [x] Create example configuration in `examples/config.yaml`
- [x] Update `.gitignore` for Python artifacts

### 1.3 Dependencies
- [x] Verify `pyproject.toml` dependencies
- [x] Generate `requirements.txt` from pyproject.toml
- [x] Test `pip install -e .` installation
  - [x] Fixed `cli()` to return proper exit code (0)
  - [x] Enhanced `activate.sh` to include installation tests
  - [x] Verified command availability and execution
  - [x] Verified Python module imports

---

## Phase 2: Core Shell Implementation

### 2.1 Configuration System (config.py)
- [x] Implement `load_config()` function
  - [x] Check `$AKUJOBIP1_CONFIG` environment variable
  - [x] Check `./akujobip1.yaml` (current directory)
  - [x] Check `~/.config/akujobip1/config.yaml` (user config)
  - [x] Fallback to built-in defaults
- [x] Implement `merge_config()` for deep merging
- [x] Implement `validate_config()` for validation
- [x] Implement `expand_paths()` for tilde expansion
- [x] Add configuration schema documentation
- [x] Write unit tests for config loading
  - [x] 39 tests implemented covering all functionality
  - [x] 92% code coverage achieved (exceeds 90% target)
  - [x] All tests passing

### 2.2 Command Parser (parser.py)
- [x] Implement `parse_command(command_line, config)` function
  - [x] Use `shlex.split()` for tokenization
  - [x] Handle quoted arguments correctly (single and double quotes)
  - [x] Handle empty input
  - [x] Handle whitespace-only input
  - [x] Handle unclosed quotes with error messages
  - [x] Integrate with wildcard expansion
- [x] Implement `expand_wildcards(args, config)` function
  - [x] Use `glob.glob()` for wildcard expansion
  - [x] Handle no matches (return literal)
  - [x] Handle multiple wildcards
  - [x] Support *, ?, and [...] wildcards
  - [x] Respect config['glob']['enabled'] setting
  - [x] Sort expansion results
- [x] Implement `_contains_wildcard()` helper function
- [x] Write comprehensive unit tests for parser
  - [x] Test quoted arguments (7 tests)
  - [x] Test wildcards (7 tests)
  - [x] Test edge cases (6 tests)
  - [x] Test configuration integration (4 tests)
  - [x] Test error handling (3 tests)
  - [x] Test integration scenarios (6 tests)
  - [x] Test real-world scenarios (6 tests)
  - [x] 56 total tests across 8 test classes
  - [x] 97% code coverage achieved (exceeds 90% target)
  - [x] All tests passing

### 2.3 Built-in Commands (builtins.py)
- [x] Create `BuiltinCommand` base class
- [x] Implement `exit` command
  - [x] Print configured exit message
  - [x] Return exit code to shell (-1 to signal termination)
- [x] Implement `cd` command
  - [x] Handle no arguments (cd to home)
  - [x] Handle directory path argument
  - [x] Handle `cd -` (previous directory)
  - [x] Error handling for invalid paths
  - [x] Optionally show pwd after cd (if configured)
- [x] Implement `pwd` command
  - [x] Print current working directory
- [x] Implement `help` command
  - [x] List available built-in commands
  - [x] Show usage information
- [x] Create `get_builtin(name)` dispatcher function
- [x] Write unit tests for each built-in
  - [x] 35 tests implemented covering all functionality
  - [x] 100% code coverage achieved (exceeds 90% target)
  - [x] All tests passing

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

**Current Status:** Phase 2.3 Complete - Built-in Commands Implemented (100% coverage, 35 tests passing)

**Completed:**

**Phase 1 - Project Setup:**
1. [x] Source directory structure created (src/akujobip1/)
2. [x] All module placeholders created with proper structure
3. [x] Configuration files created (akujobip1.yaml, examples/config.yaml)
4. [x] Dependencies verified and requirements.txt generated
5. [x] All modules compile successfully
6. [x] Installation tested and verified working (`pip install -e .`)
7. [x] Entry point (`akujobip1` command) working correctly

**Phase 2.1 - Configuration System:**
8. [x] Implemented `get_default_config()` with complete default configuration
9. [x] Implemented `merge_config()` with recursive deep merging algorithm
10. [x] Implemented `expand_paths()` for tilde and environment variable expansion
11. [x] Implemented `validate_config()` with comprehensive validation rules
12. [x] Implemented `load_yaml_file()` with error handling
13. [x] Implemented `load_config()` with 4-level priority loading
14. [x] Created comprehensive test suite (39 tests, 6 test classes)
15. [x] Achieved 92% code coverage (exceeds 90% target)
16. [x] Updated changelog with Phase 2.1 completion
17. [x] Updated version to 0.2.0

**Phase 2.2 - Command Parser:**
18. [x] Implemented `parse_command()` with shlex tokenization and quote handling
19. [x] Implemented `expand_wildcards()` with glob pattern matching
20. [x] Implemented `_contains_wildcard()` helper function
21. [x] Integrated parser with configuration system
22. [x] Added comprehensive error handling (unclosed quotes, empty input)
23. [x] Created comprehensive test suite (56 tests, 8 test classes)
24. [x] Achieved 97% code coverage (exceeds 90% target)
25. [x] Updated changelog with Phase 2.2 completion
26. [x] Updated version to 0.3.0

**Phase 2.3 - Built-in Commands:**
27. [x] Implemented `BuiltinCommand` base class
28. [x] Implemented `ExitCommand` with configurable message
29. [x] Implemented `CdCommand` with home, paths, cd -, and error handling
30. [x] Implemented `PwdCommand` to print working directory
31. [x] Implemented `HelpCommand` to show available commands
32. [x] Implemented `get_builtin()` dispatcher function
33. [x] Created comprehensive test suite (35 tests, 12 test classes)
34. [x] Achieved 100% code coverage (exceeds 90% target)
35. [x] Updated changelog with Phase 2.3 completion
36. [x] Updated version to 0.4.0

**Next Steps:**
1. Phase 2.4: Implement process executor (executor.py)
2. Phase 2.5: Implement main shell loop (shell.py)
3. Phase 3: Error handling and edge cases
4. Phase 4: Testing (integration and bash tests)

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
