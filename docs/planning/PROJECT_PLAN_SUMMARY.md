# AkujobiP1Shell - Project Plan Summary

**CSC456 Programming Assignment 1**
**Author:** John Akujobi
**Date:** 2025-11-09
**Planning Phase:** Complete

---

## Executive Summary

This document provides a comprehensive overview of the planning phase for the AkujobiP1Shell project, a simple POSIX-compliant shell implementation for CSC456.

### Project Goals
1. Demonstrate process management using system calls (fork, exec, wait)
2. Implement a working command-line interpreter
3. Achieve 95-100% grade through comprehensive implementation, testing, and documentation

### Current Status
**Planning Phase:** COMPLETE
**Implementation Phase:** READY TO BEGIN

---

## Planning Documents Created

### 1. Requirements Analysis
**File:** `docs/planning/requirements_analysis.md`
**Size:** 40+ pages
**Purpose:** Comprehensive analysis of all requirements with options, pros/cons, and decisions

**Key Sections:**
- Implementation language and environment (Python 3.10+, Linux primary)
- Core functionality scope (built-ins + external commands)
- Error handling strategy (comprehensive coverage)
- Process management details (fork/execvp/waitpid)
- Testing strategy (90%+ coverage target)
- Documentation requirements (diagrams, walkthrough, screenshots)
- Configuration system (YAML-based)
- Submission format (Git release + zip file)

**Key Decisions:**
- Python implementation (already configured, faster development)
- Support built-in commands (cd, exit, pwd, help) AND external commands
- Use `execvp()` for PATH search capability
- Configurable exit code display (on_failure by default)
- YAML configuration with priority: env var > current dir > user home > defaults
- No I/O redirection or pipes (out of scope)
- Wildcard expansion supported (*.txt, etc.)
- Comprehensive error handling (display and continue)

---

### 2. Implementation Checklist
**File:** `docs/planning/implementation_checklist.md`
**Size:** 400+ action items
**Purpose:** Step-by-step checklist for implementation

**Phases:**
1. **Project Setup** - Directory structure, configuration files
2. **Core Implementation** - Config, parser, built-ins, executor, main loop
3. **Error Handling** - Edge cases, error messages
4. **Testing** - Unit tests (35+), bash tests, coverage
5. **CI/CD** - GitHub Actions workflow
6. **Documentation** - Diagrams, report, README
7. **Final Polish** - Code review, verification
8. **Submission** - Git release, zip file

**Progress Tracking:** Each phase has detailed sub-tasks with checkboxes

---

### 3. Technical Specification
**File:** `docs/planning/technical_specification.md`
**Size:** 30+ pages
**Purpose:** Detailed technical design and API documentation

**Key Sections:**
- System architecture diagrams
- Module specifications (shell.py, config.py, parser.py, builtins.py, executor.py)
- API documentation with function signatures
- Data structures (configuration dict, command args)
- Process flow diagrams (startup, execution, fork/exec/wait)
- Error handling strategy with exit codes
- Configuration schema
- Testing strategy

**Implementation Details:**
- Pseudocode for all major functions
- Class hierarchies (BuiltinCommand base class)
- Signal handling approach (SIGINT, EOF)
- Exit status handling (POSIX standard codes)
- Configuration loading priority order

---

## Project Structure

```
AkujobiP1Shell/
├── src/
│   └── akujobip1/              # Main package (TO BE CREATED)
│       ├── __init__.py         # Package initialization
│       ├── shell.py            # Main shell loop, entry point
│       ├── config.py           # Configuration management
│       ├── parser.py           # Command parsing
│       ├── builtins.py         # Built-in commands
│       └── executor.py         # External command execution
├── tests/
│   ├── test_shell.py           # Pytest tests (TO BE IMPLEMENTED)
│   ├── test_config.py          # Config tests
│   ├── test_parser.py          # Parser tests
│   ├── test_builtins.py        # Built-in tests
│   ├── test_executor.py        # Executor tests
│   └── run_tests.sh            # Bash tests (EXISTING)
├── docs/
│   ├── planning/
│   │   ├── requirements_analysis.md
│   │   ├── implementation_checklist.md
│   │   ├── technical_specification.md
│   │   └── PROJECT_PLAN_SUMMARY.md (this file)
│   ├── report.md               # Final report (TO BE CREATED)
│   ├── architecture_diagram.png (TO BE CREATED)
│   └── syscall_flow_diagram.png (TO BE CREATED)
├── .github/
│   └── workflows/
│       └── ci.yml              # CI/CD pipeline (TO BE UPDATED)
├── pyproject.toml              # Python project config (EXISTING)
├── akujobip1.yaml              # Example config (TO BE CREATED)
└── README.md                   # Project README (TO BE UPDATED)
```

---

## Implementation Approach

### Architecture Overview

The shell is designed with a modular architecture:

1. **Main Loop (shell.py)**
   - Displays prompt: `AkujobiP1> `
   - Reads user input
   - Handles signals (Ctrl+C, Ctrl+D)
   - Coordinates other modules

2. **Configuration System (config.py)**
   - Loads YAML configuration
   - Merges with defaults
   - Provides runtime settings

3. **Command Parser (parser.py)**
   - Tokenizes input using `shlex.split()`
   - Expands wildcards using `glob`
   - Handles quoted arguments

4. **Built-in Dispatcher (builtins.py)**
   - Implements: exit, cd, pwd, help
   - Returns exit codes
   - Handles built-in specific errors

5. **External Executor (executor.py)**
   - Implements fork/exec/wait pattern
   - Handles command not found errors
   - Displays exit codes (configurable)

### Process Management Flow

```
User Command → Parse → Built-in?
                          ├─ Yes → Execute in shell process
                          └─ No  → Fork → Child: execvp()
                                        → Parent: waitpid()
                                        → Display result
```

### Key Features

**Core Requirements:**
- Custom prompt: `AkujobiP1> `
- Execute any Linux/Unix commands
- Support unlimited arguments (tested with 1-3)
- Parent waits for child completion
- Exit command with "Bye!" message
- POSIX-compliant

**Enhanced Features:**
- Built-in commands (cd, pwd, help)
- Quoted argument support ("hello world")
- Wildcard expansion (*.txt)
- Configurable via YAML
- Graceful error handling
- Signal handling (Ctrl+C kills child only)
- EOF handling (Ctrl+D exits gracefully)
- Exit code display (configurable)

---

## Testing Strategy

### Test Coverage Target: 90%+

**Unit Tests (pytest):**
- Configuration loading and merging
- Command parsing (quotes, wildcards)
- Built-in commands (all variants)
- External command execution (mocked)
- Error handling (all error types)
- Signal handling

**Integration Tests (bash):**
- Exit command
- Empty input handling
- Unknown command error
- Quoted arguments

**Manual Tests:**
- Real command execution on Ubuntu
- Interactive signal testing
- Configuration variations
- Performance (100+ commands)

### CI/CD Pipeline

**GitHub Actions:**
- Python 3.10 setup
- Dependency installation
- Pytest with coverage reporting
- Bash test suite
- Code linting (ruff)
- Code formatting check (black)

---

## Documentation Plan

### Report Contents

**1. Architecture Diagram**
- Component diagram showing modules
- Data flow diagram

**2. System Call Flow Diagram**
- Sequence diagram for fork/exec/wait
- Process creation and termination

**3. Code Walkthrough**
- Main loop explanation
- Command parsing
- Built-in dispatcher
- External execution
- Error handling
- Configuration system
- Signal handling

**4. Screenshots (10+)**
- Shell startup
- Simple commands
- Multi-argument commands
- Built-in commands
- Error handling
- Exit command
- Ctrl+C handling
- Wildcard expansion
- Configuration
- Test execution

### README Structure

- Project description
- Features list
- Requirements (Python 3.10+, Linux)
- Installation (`pip install -e .`)
- Usage examples
- Configuration documentation
- Built-in commands reference
- Testing instructions
- Development guide

---

## Configuration System

### YAML Configuration File

**Default Location Priority:**
1. `$AKUJOBIP1_CONFIG` environment variable
2. `./akujobip1.yaml` (current directory)
3. `~/.config/akujobip1/config.yaml`
4. Built-in defaults

**Configurable Options:**
- Prompt text
- Exit message
- Exit code display (never/on_failure/always)
- Exit code format
- Wildcard expansion (enable/disable)
- Built-in command options
- Debug settings (logging, verbose errors)

**Example Configuration:**
```yaml
prompt:
  text: "AkujobiP1> "

exit:
  message: "Bye!"

execution:
  show_exit_codes: "on_failure"
  exit_code_format: "[Exit: {code}]"

glob:
  enabled: true

debug:
  log_commands: false
  show_fork_pids: false
```

---

## Submission Requirements

### Deliverables

**1. Git Release (v1.0.0)**
- Tagged release on GitHub
- Release notes with feature summary
- Attached zip file

**2. Zip File: `CSC456_ProAssgn1_Akujobi.zip`**
Contents:
- Source code (`src/akujobip1/`)
- Test files (`tests/`)
- Documentation (`docs/`, README.md)
- Configuration files (pyproject.toml, akujobip1.yaml)
- Report (docs/report.md or report.pdf)
- Requirements.txt

**3. Installation Method**
- `pip install -e .` (development mode)
- Creates `akujobip1` command
- Alternative: `python -m akujobip1`

**No Makefile Required:**
- Python doesn't need compilation
- pyproject.toml is the standard
- Optional Makefile for convenience commands only

---

## Evaluation Criteria Alignment

### Documentation (20%)
**Our Approach:**
- Comprehensive report with all required sections
- Architecture and system call flow diagrams
- Detailed code walkthrough
- 10+ screenshots showing all features
- Complete README with usage instructions
- Well-commented code (Google-style docstrings)

**Expected Score:** 19-20/20

---

### Compilation (15%)
**Our Approach:**
- Clean `pip install -e .` installation
- No errors or warnings
- Automated CI testing
- Works on Ubuntu (primary target)

**Expected Score:** 14-15/15

---

### Correctness (60%)
**Our Approach:**
- All core requirements implemented
- 35+ pytest tests (90%+ coverage)
- All 4 bash tests passing
- Proper fork/exec/wait implementation
- Correct error handling
- POSIX-compliant exit codes

**Requirements Met:**
- Display prompt: `AkujobiP1> ` ✓
- Execute commands with arguments ✓
- Support 1-3 arguments (unlimited supported) ✓
- Exit command with "Bye!" ✓
- Parent waits for child ✓
- POSIX-compliant ✓

**Expected Score:** 57-60/60

---

### Readability & Misc (5%)
**Our Approach:**
- Black formatting (consistent style)
- Comprehensive inline comments
- Clear variable/function names
- Proper zip file naming
- All necessary files included
- No emojis in code/docs

**Expected Score:** 5/5

---

### TOTAL EXPECTED GRADE: 95-100/100 (A)

---

## Risk Assessment

### Low Risks
- Python implementation (well-supported, documented)
- Standard library usage (no external dependencies for runtime)
- Configuration system (PyYAML is stable)

### Medium Risks
- Test coverage target (90%+) - requires comprehensive test writing
- CI pipeline configuration - needs proper setup
- Documentation completeness - time-intensive

### Mitigation Strategies
- Start with core functionality, add features incrementally
- Write tests alongside implementation
- Use automated tools (black, ruff) for code quality
- Create documentation templates early

---

## Timeline Estimate

### Phase 1: Core Implementation (Week 1)
**Days 1-2:** Configuration system and parser
**Days 3-4:** Built-in commands and executor
**Day 5:** Main shell loop and signal handling

### Phase 2: Testing (Week 2)
**Days 1-2:** Write pytest tests (35+ cases)
**Day 3:** Fix bugs, improve coverage
**Day 4:** Verify bash tests pass
**Day 5:** CI/CD pipeline setup

### Phase 3: Documentation (Week 3)
**Day 1:** Create diagrams
**Days 2-3:** Write report (code walkthrough)
**Day 4:** Screenshots and README
**Day 5:** Review and polish

### Phase 4: Submission (Week 4)
**Day 1:** Create submission zip
**Day 2:** Git release
**Day 3:** Final testing on clean Ubuntu
**Days 4-5:** Buffer for issues

**Total Time:** 3-4 weeks

---

## Next Steps

### Immediate Actions (Ready to Start)

1. **Create Source Directory Structure**
   ```bash
   mkdir -p src/akujobip1
   touch src/akujobip1/__init__.py
   ```

2. **Implement Configuration System**
   - Start with `config.py`
   - Define default configuration
   - Implement load_config() function

3. **Implement Command Parser**
   - Create `parser.py`
   - Implement parse_command() with shlex
   - Add wildcard expansion

4. **Implement Built-in Commands**
   - Create `builtins.py`
   - Implement BuiltinCommand base class
   - Implement exit, cd, pwd, help

5. **Implement External Executor**
   - Create `executor.py`
   - Implement fork/exec/wait pattern
   - Add error handling

6. **Implement Main Shell Loop**
   - Create `shell.py`
   - Implement cli() entry point
   - Add signal handlers
   - Implement REPL loop

7. **Write Tests**
   - Create test files for each module
   - Achieve 90%+ coverage
   - Verify bash tests pass

8. **Create Documentation**
   - Generate diagrams
   - Write report
   - Update README
   - Take screenshots

9. **Final Polish**
   - Lint and format code
   - Review documentation
   - Create submission zip
   - Publish Git release

---

## Questions for User

Before beginning implementation, please confirm:

1. **Scope Confirmation:**
   - Are you satisfied with the planned features?
   - Any features to add/remove?

2. **Testing Approach:**
   - 90%+ coverage target acceptable?
   - Additional test cases needed?

3. **Documentation Level:**
   - Report detail level appropriate?
   - Any additional diagrams/screenshots needed?

4. **Timeline:**
   - Is 3-4 week timeline acceptable?
   - Any specific deadline?

5. **Implementation Priority:**
   - Should we implement in the order listed?
   - Any high-priority features?

---

## Conclusion

Planning phase is complete with comprehensive documentation covering:
- All requirements analyzed with decisions made
- Detailed technical specifications
- Step-by-step implementation checklist
- Testing strategy defined
- Documentation plan established

**Status:** READY TO IMPLEMENT

**Recommendation:** Review planning documents, confirm scope, then proceed with implementation following the checklist in order.

---

**Document Version:** 1.0
**Last Updated:** 2025-11-09
**Status:** Complete - Ready for User Review
