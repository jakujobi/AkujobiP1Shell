# Changelog

## [0.2.0] - 2025-11-10

### Phase 2.1: Configuration System Implementation - COMPLETED

#### Overview
Implemented complete configuration management system with YAML support, deep merging, path expansion, and comprehensive validation. The system supports multiple configuration sources with proper priority ordering.

#### Implementation Approach
After analyzing three different approaches (simple sequential loading, recursive deep merge, and schema-based validation), chose **Approach 2: Recursive Deep Merge** for its correctness, maintainability, and lack of external dependencies beyond PyYAML.

**Key Design Decisions:**
- Deep recursive merging preserves nested configuration structure
- Partial overrides don't lose sibling settings
- Graceful degradation when YAML files are missing or invalid
- Validation warns but never crashes - always returns valid configuration

#### Functions Implemented (config.py)

**`get_default_config() -> Dict[str, Any]`**
- Returns complete default configuration dictionary
- Includes all settings: prompt, exit, execution, glob, builtins, errors, debug
- Creates new dict each call (no shared state)

**`merge_config(base, override) -> Dict[str, Any]`**
- Recursive deep merge algorithm
- Preserves nested keys from both base and override
- Override values take precedence
- Handles dicts, lists, and primitives correctly
- Returns new dict (doesn't modify originals)

**`expand_paths(config) -> Dict[str, Any]`**
- Expands tilde (~) to user home directory
- Expands environment variables ($VAR)
- Recursively processes nested dictionaries
- Only expands strings containing ~ or $

**`validate_config(config) -> bool`**
- Validates required keys (prompt.text, exit.message)
- Validates enum values (show_exit_codes: never/on_failure/always)
- Validates boolean fields throughout config
- Prints warnings to stderr but always returns True
- Never crashes on invalid config

**`load_yaml_file(filepath) -> Optional[Dict[str, Any]]`**
- Loads and parses YAML file safely
- Returns None for missing files (not an error)
- Handles YAML parsing errors gracefully
- Validates file contains dictionary
- Returns {} for empty files

**`load_config() -> Dict[str, Any]`**
- Implements 4-level priority configuration loading:
  1. Built-in defaults (lowest priority)
  2. `~/.config/akujobip1/config.yaml` (user config)
  3. `./akujobip1.yaml` (current directory)
  4. `$AKUJOBIP1_CONFIG` environment variable (highest priority)
- Each level merges with previous levels
- Missing files silently skipped
- Expands all paths after loading
- Validates final configuration

#### Test Coverage (tests/test_config.py)

**Total Tests: 39 tests across 6 test classes**
**Coverage: 92% (exceeds 90% target)**

**Test Classes:**
1. **TestDefaultConfig** (7 tests)
   - Structure validation
   - Individual setting verification
   - Immutability checks

2. **TestMergeConfig** (8 tests)
   - Simple overrides
   - Nested partial overrides
   - Deep nesting preservation
   - New key addition
   - Original dict protection
   - List replacement
   - Type conversion handling

3. **TestExpandPaths** (5 tests)
   - Tilde expansion
   - Environment variable expansion
   - Nested path expansion
   - Non-path preservation
   - Type preservation

4. **TestValidateConfig** (6 tests)
   - Valid configuration acceptance
   - Missing key detection
   - Invalid enum value detection
   - Valid enum value verification
   - Type validation

5. **TestLoadYamlFile** (5 tests)
   - Valid YAML loading
   - Missing file handling
   - Empty file handling
   - Invalid YAML handling
   - Non-dict YAML handling

6. **TestLoadConfig** (8 tests)
   - Defaults-only loading
   - Local config loading
   - Environment variable priority
   - Partial override merging
   - Path expansion integration
   - Invalid config handling
   - User config directory support
   - Multiple config merging

#### Configuration Schema

```yaml
prompt:
  text: string                    # Default: "AkujobiP1> "

exit:
  message: string                 # Default: "Bye!"

execution:
  show_exit_codes: enum          # never | on_failure | always
  exit_code_format: string       # Default: "[Exit: {code}]"

glob:
  enabled: boolean               # Default: true
  show_expansions: boolean       # Default: false

builtins:
  cd:
    enabled: boolean             # Default: true
    show_pwd_after: boolean      # Default: false
  pwd:
    enabled: boolean             # Default: true
  help:
    enabled: boolean             # Default: true

errors:
  verbose: boolean               # Default: false

debug:
  log_commands: boolean          # Default: false
  log_file: string               # Default: "~/.akujobip1.log"
  show_fork_pids: boolean        # Default: false
```

#### Quality Metrics
- **Lines of Code**: 269 lines (config.py)
- **Test Code**: 505 lines (test_config.py)
- **Test Coverage**: 92% (39/39 tests passing)
- **Missing Coverage**: Only edge cases (PyYAML not installed warning, rare error paths)
- **Code Quality**: No linter errors
- **Documentation**: Complete docstrings with examples

#### Dependencies
- **PyYAML >= 6.0**: YAML parsing (already in pyproject.toml)
- **pytest-cov**: Code coverage analysis (development only)

#### Benefits Delivered
1. **Flexible Configuration**: Users can customize any setting without affecting others
2. **Multiple Sources**: Support for user-wide, project-local, and environment-specific configs
3. **Safe Defaults**: Always provides working configuration even if all files missing
4. **Clear Priority**: Environment > Local > User > Default
5. **Validation**: Catches configuration errors early with helpful warnings
6. **Path Expansion**: Automatic tilde and environment variable expansion
7. **Professional Quality**: Production-ready deep merge algorithm
8. **Well-Tested**: 92% coverage with comprehensive edge case testing

#### Next Steps
- Phase 2.2: Command Parser (parser.py)
- Phase 2.3: Built-in Commands (builtins.py)
- Phase 2.4: Process Executor (executor.py)
- Phase 2.5: Main Shell Loop (shell.py)

---

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
