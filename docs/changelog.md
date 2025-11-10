# Changelog

## [0.1.0] - 2025-11-10

### Phase 1: Project Setup and Core Structure - COMPLETED

#### Directory Structure Created
- Created `src/akujobip1/` package directory
- Created `src/akujobip1/__init__.py` (9 lines) - Package initialization with version info
- Created `src/akujobip1/shell.py` (58 lines) - Main shell loop and entry point placeholder
- Created `src/akujobip1/config.py` (83 lines) - Configuration management placeholder
- Created `src/akujobip1/builtins.py` (82 lines) - Built-in commands placeholder
- Created `src/akujobip1/executor.py` (45 lines) - Process execution placeholder
- Created `src/akujobip1/parser.py` (41 lines) - Command parsing placeholder

#### Configuration Files
- Created `akujobip1.yaml` - Default configuration file with all settings
- Created `examples/config.yaml` - Example configuration with detailed comments
- Configuration includes: prompt customization, exit message, execution settings, glob support, builtin commands, error handling, and debug options

#### Dependencies
- Updated `pyproject.toml` to include `PyYAML>=6.0` as a dependency
- Generated `requirements.txt` with PyYAML dependency
- Verified Python 3.10+ requirement
- All modules compile successfully without errors

#### Validation Results
- Total lines of code: 318 lines across all modules
- All files under 300 lines limit (largest: config.py at 83 lines, builtins.py at 82 lines)
- All Python modules compile without syntax errors
- All required files present and properly structured
- .gitignore already covers Python artifacts (no changes needed)

#### Module Structure
Each placeholder module includes:
- Function signatures matching technical specification
- TODO comments for implementation guidance
- Google-style docstrings
- Type hints for parameters and return values
- Proper imports and dependencies

#### Next Steps
- Phase 2: Core Shell Implementation (config, parser, builtins, executor, main loop)
- Phase 3: Error Handling and Edge Cases
- Phase 4: Testing (unit tests and bash tests)

---

## [0.1.0-initial] - 2024-10-08

### Added
- Project structure and configuration setup
- Python package configuration (pyproject.toml) for AkujobiP1 shell
- Basic test framework with shell behavior tests
- Core requirements documentation
- Project planning documentation

### Project Setup
- **Package Name**: AkujobiP1 (CSC456 Process Management Shell)
- **Description**: POSIX syscalls in Python implementation
- **Author**: John Akujobi (jakujobi.com, john@jakujobi.com)
- **Python Version**: >= 3.10

### Features Planned
- Command-line shell with "AkujobiP1> " prompt
- Support for arbitrary Linux/Unix commands with arguments
- Process management using exec() system calls
- Exit command handling with "Bye!" message
- Child process synchronization (wait for completion)
- POSIX-compliant operation

### Test Suite
- Exit command functionality test
- Empty input handling test
- Unknown command error handling test
- Quoted arguments support test

### Documentation
- Core requirements specification in `docs/planning/core_req.md`
- Project structure and build configuration
- Test framework setup with expected behaviors

*Note: This is the initial project setup. The actual shell implementation is pending.*
