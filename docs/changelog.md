# Changelog

## [0.1.0] - 2024-10-08

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
