# Changelog

## [0.1.1] - 2025-11-10

### Phase 1.4: Code Quality and Consistency Fixes - COMPLETED

#### Version Consistency
- Updated version number to 0.1.1 across all files
- Fixed `src/akujobip1/__init__.py` to match pyproject.toml version
- Ensures consistent versioning during packaging and deployment

#### Installation Script Improvements
- Fixed duplicate step counter [2/7] in `activate.sh`
- Removed step number from conditional cleanup step for clarity
- Fixed unreachable code in installation test logic (line 158)
- Simplified exit code handling in test validation
- Step counter now sequential: [1/7] through [7/7]

#### Type Contract Fixes
Fixed type contract violations across all modules where placeholder functions returned None instead of declared types:

**builtins.py**
- Fixed `ExitCommand.execute()` to raise NotImplementedError
- Fixed `CdCommand.execute()` to raise NotImplementedError
- Fixed `PwdCommand.execute()` to raise NotImplementedError
- Fixed `HelpCommand.execute()` to raise NotImplementedError

**config.py**
- Fixed `load_config()` to raise NotImplementedError
- Fixed `merge_config()` to raise NotImplementedError
- Fixed `validate_config()` to raise NotImplementedError
- Fixed `get_default_config()` to raise NotImplementedError
- Fixed `expand_paths()` to raise NotImplementedError

**executor.py**
- Fixed `execute_external_command()` to raise NotImplementedError
- Fixed `display_exit_status()` to raise NotImplementedError

**parser.py**
- Fixed `parse_command()` to raise NotImplementedError
- Fixed `expand_wildcards()` to raise NotImplementedError

**shell.py**
- Fixed `run_shell()` to raise NotImplementedError
- Fixed `setup_signal_handlers()` to raise NotImplementedError
- Fixed `sigint_handler()` to raise NotImplementedError

#### Benefits
- All type hints now correctly represent function behavior
- Static analysis tools will no longer flag these violations
- Clear indication that functions are placeholder stubs
- Consistent with Phase 1 installation review fixes
- Prevents unexpected None returns during integration

---

### Phase 1.3: Installation Testing and Fixes - COMPLETED

#### Fixed Installation Issues
- Fixed `cli()` function in `shell.py` to return proper exit code (0) instead of None
- Added temporary startup message to verify installation works
- Function now correctly implements its type signature (returns int)

#### Enhanced Installation Testing
- Updated `activate.sh` to include comprehensive installation tests (step 7/7)
- Added verification that `akujobip1` command is available in PATH
- Added verification that command executes successfully and returns exit code 0
- Added verification that Python module can be imported correctly
- Installation now fails fast if command is not found after installation

#### Installation Test Coverage
- Command availability test (checks PATH)
- Command execution test (verifies it runs and returns 0)
- Module import test (verifies Python can import akujobip1.shell.cli)
- All tests run automatically during setup

#### Updated Documentation
- Marked Phase 1.3 dependencies as complete in implementation checklist
- Added detailed sub-items showing what was tested
- Updated progress tracking to include installation verification
- Verified Phase 1 is now fully complete and ready for Phase 2

---

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
