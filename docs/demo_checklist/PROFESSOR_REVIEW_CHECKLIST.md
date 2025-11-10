# CSC456 Programming Assignment 1 - Professor's Review Checklist

**Course:** CSC456 - Operating Systems
**Assignment:** Process Management Shell
**Student:** John Akujobi
**Reviewer Role:** Course Instructor
**Date:** 2025-11-09

---

## Table of Contents

1. [Introduction](#introduction)
2. [Expected Live Demonstration](#expected-live-demonstration)
3. [Critical Questions for Student](#critical-questions-for-student)
4. [Code Review Checklist](#code-review-checklist)
5. [Testing Scenarios](#testing-scenarios)
6. [Grading Rubric (Detailed)](#grading-rubric-detailed)
7. [Edge Cases & Stress Testing](#edge-cases--stress-testing)
8. [Documentation Review](#documentation-review)
9. [Final Assessment Questions](#final-assessment-questions)

---

## Introduction

As your professor, I will be evaluating this assignment based on the following criteria:

- **Documentation (20%):** Does the report clearly explain the implementation?
- **Compilation (15%):** Does the code compile/run without errors or warnings?
- **Correctness (60%):** Does the program meet ALL functional requirements?
- **Readability & Misc (5%):** Is the code well-commented and properly submitted?

This review document outlines what I expect to see during your demonstration, the questions I will ask, and the testing scenarios I will execute to verify your implementation.

**Important:** I will not only test the "happy path" but also edge cases, error conditions, and scenarios that might break a poorly implemented shell.

---

## Expected Live Demonstration

During your submission review or oral examination, I expect you to demonstrate the following scenarios **live** on your system.

### Demonstration Scenario 1: Basic Shell Startup and Exit

**What I will ask you to show:**

```bash
# Start the shell
./activate.sh
akujobip1
```

**Expected Behavior:**
- Shell displays the prompt: `AkujobiP1> `
- Shell waits for user input
- No error messages during startup
- Configuration loads successfully (if verbose mode enabled, show config loading)

**Then test exit:**

```bash
AkujobiP1> exit
```

**Expected Behavior:**
- Shell prints: `Bye!` (or configured exit message)
- Shell terminates with exit code 0
- Process returns control to parent shell

**Questions I will ask:**
1. What system calls are involved in starting your shell?
2. How does your shell know when to terminate?
3. Where is the exit message configured?

---

### Demonstration Scenario 2: Simple Commands with Arguments

**What I will ask you to show:**

```bash
AkujobiP1> ls
AkujobiP1> ls -l
AkujobiP1> ls -la
AkujobiP1> pwd
AkujobiP1> echo hello
AkujobiP1> echo hello world
```

**Expected Behavior:**
- Each command executes correctly
- Output appears immediately after command
- Prompt returns after each command completes
- No zombie processes left behind

**Questions I will ask:**
1. Walk me through the system calls used to execute `ls -la`
2. How does your shell pass arguments to the child process?
3. What happens in the parent process while the child is running?
4. Show me in the code where you call `fork()`, `exec()`, and `wait()`

---

### Demonstration Scenario 3: Commands with Multiple Arguments

**What I will ask you to show:**

```bash
AkujobiP1> cp /tmp/test1.txt /tmp/test2.txt
AkujobiP1> mkdir /tmp/testdir1 /tmp/testdir2 /tmp/testdir3
AkujobiP1> rm -rf /tmp/testdir1
AkujobiP1> grep -r "pattern" /tmp/
```

**Expected Behavior:**
- Commands with 2, 3, and more arguments work correctly
- Arguments are passed in the correct order
- Commands modify the filesystem as expected

**Questions I will ask:**
1. How do you parse multiple arguments from user input?
2. What data structure do you use to store arguments?
3. How do you handle arguments with spaces or special characters?

---

### Demonstration Scenario 4: Quoted Arguments

**What I will ask you to show:**

```bash
AkujobiP1> echo "hello world"
AkujobiP1> echo 'single quotes'
AkujobiP1> mkdir "directory with spaces"
AkujobiP1> ls -l "directory with spaces"
AkujobiP1> echo "nested 'quotes' test"
```

**Expected Behavior:**
- Quoted strings are treated as single arguments
- Both single and double quotes work
- Quotes are not passed to the command
- Nested quotes are handled correctly

**Questions I will ask:**
1. What parsing library/method do you use for quoted arguments?
2. Why is handling quotes important for a shell?
3. What's the difference between single and double quotes in your implementation?

---

### Demonstration Scenario 5: Error Handling - Command Not Found

**What I will ask you to show:**

```bash
AkujobiP1> nonexistentcommand
AkujobiP1> /usr/bin/fakecmd
AkujobiP1> ./missingfile
```

**Expected Behavior:**
- Shell prints appropriate error message (e.g., "Command not found")
- Error goes to stderr, not stdout
- Shell does NOT crash or exit
- Prompt returns for next command
- Exit status should be 127 (command not found)

**Questions I will ask:**
1. How do you detect that a command doesn't exist?
2. What exit code do you return for command not found? Why?
3. How do you prevent the shell from crashing when exec() fails?
4. Show me the error handling code in your executor module

---

### Demonstration Scenario 6: Built-in Commands

**What I will ask you to show:**

```bash
AkujobiP1> pwd
AkujobiP1> cd /tmp
AkujobiP1> pwd
AkujobiP1> cd
AkujobiP1> pwd
AkujobiP1> cd -
AkujobiP1> help
AkujobiP1> exit
```

**Expected Behavior:**
- Built-in commands execute without forking
- `cd` changes the shell's working directory
- `pwd` shows current directory
- `help` lists available commands
- `exit` terminates the shell

**Questions I will ask:**
1. Why can't `cd` be an external command?
2. How do you distinguish between built-in and external commands?
3. Show me where you dispatch to built-in vs external execution
4. What happens if I try to fork for a `cd` command?

---

### Demonstration Scenario 7: Signal Handling (Ctrl+C)

**What I will ask you to show:**

```bash
AkujobiP1> sleep 10
^C
AkujobiP1> echo "still alive"
```

**Expected Behavior:**
- Ctrl+C interrupts the running command (`sleep`)
- Shell itself does NOT terminate
- New prompt appears immediately
- Next command executes normally

**Then test Ctrl+C at empty prompt:**

```bash
AkujobiP1> ^C
AkujobiP1>
```

**Expected Behavior:**
- Pressing Ctrl+C at prompt shows new prompt
- Shell does not exit

**Questions I will ask:**
1. What signal is sent when user presses Ctrl+C?
2. How do you handle SIGINT in the parent process?
3. How do you ensure the child process CAN be interrupted?
4. Show me your signal handler code
5. What's the difference between signal handling in parent vs child?

---

### Demonstration Scenario 8: Wildcard Expansion

**What I will ask you to show:**

```bash
AkujobiP1> ls *.py
AkujobiP1> echo src/**/*.py
AkujobiP1> rm /tmp/test*.txt
AkujobiP1> cp *.md /tmp/
```

**Expected Behavior:**
- Wildcards expand to matching files
- If no matches, behavior should be sensible (keep literal or error)
- Multiple wildcards in one command work
- Recursive wildcards work if supported

**Questions I will ask:**
1. Who performs wildcard expansion - the shell or the command?
2. What happens if a wildcard matches nothing?
3. How do you implement glob expansion?
4. Can users disable glob expansion? How?

---

### Demonstration Scenario 9: Parent Waiting for Child

**What I will ask you to show:**

```bash
AkujobiP1> sleep 5
# (wait 5 seconds)
AkujobiP1>
```

**Expected Behavior:**
- Shell waits for `sleep 5` to complete
- Prompt does NOT appear until command finishes
- No zombie processes created

**Questions I will ask:**
1. Show me where you call `waitpid()` or `wait()`
2. What happens if you don't wait for the child?
3. What is a zombie process?
4. How do you extract the exit status from the child?

---

### Demonstration Scenario 10: Rapid Command Execution

**What I will ask you to show:**

```bash
AkujobiP1> echo 1; echo 2; echo 3
# OR execute commands rapidly
AkujobiP1> pwd
AkujobiP1> ls
AkujobiP1> date
AkujobiP1> whoami
AkujobiP1> hostname
```

**Expected Behavior:**
- All commands execute correctly
- No race conditions
- No memory leaks
- Consistent behavior

**Questions I will ask:**
1. Can your shell handle rapid command execution?
2. Do you have any resource leaks?
3. How do you ensure cleanup after each command?

---

## Critical Questions for Student

### Section A: Process Management Understanding

**Q1:** Explain the entire lifecycle of a command execution in your shell, from when the user presses Enter to when the prompt returns. Include all system calls.

**What I'm looking for:**
- Mention of `fork()`
- Mention of `exec()` family (execvp, execve, etc.)
- Mention of `wait()` or `waitpid()`
- Understanding of parent/child relationship
- Knowledge of exit status handling

---

**Q2:** What is the difference between `fork()` and `exec()`? Why do you need both?

**What I'm looking for:**
- `fork()` creates a new process (copy of parent)
- `exec()` replaces process image with new program
- You need fork to create child, then exec to run different program
- Understanding of process address space

---

**Q3:** What happens if `fork()` fails? How do you handle this?

**What I'm looking for:**
- fork() returns -1 on failure
- Reasons for failure (system resource limits, ulimits)
- Error handling code
- Graceful degradation

---

**Q4:** What happens if `exec()` fails? How do you handle this?

**What I'm looking for:**
- exec() only returns if it fails
- Child process must handle the error
- Child must exit with appropriate code (127 or 126)
- Parent must not continue executing shell code in child

---

**Q5:** Explain the difference between `execv()`, `execvp()`, `execve()`, and `execl()`. Which did you choose and why?

**What I'm looking for:**
- Understanding of different exec variants
- Knowledge that 'p' searches PATH
- Knowledge that 'v' takes array, 'l' takes list
- Knowledge that 'e' takes environment
- Justification for choice (likely execvp for PATH search)

---

**Q6:** What is a zombie process? How do you prevent creating them?

**What I'm looking for:**
- Zombie = terminated child whose status hasn't been read by parent
- Prevented by calling wait() or waitpid()
- Understanding that zombies consume process table entries
- Knowledge of SIGCHLD signal (bonus)

---

### Section B: Implementation Details

**Q7:** Walk me through your code: show me exactly where you call fork(), exec(), and wait().

**What I'm looking for:**
- Ability to navigate codebase
- Clear understanding of code flow
- Proper error handling at each step

---

**Q8:** How do you distinguish between built-in commands (like `cd`) and external commands (like `ls`)?

**What I'm looking for:**
- Check against list of built-ins first
- Dispatch mechanism
- Understanding that built-ins must run in parent process

---

**Q9:** How do you parse the user's command line input? What edge cases do you handle?

**What I'm looking for:**
- Use of parsing library (shlex) or manual parsing
- Handling of quotes, escapes, whitespace
- Edge cases: empty input, whitespace-only, unclosed quotes

---

**Q10:** How does your configuration system work? What can be configured?

**What I'm looking for:**
- Configuration file locations
- Priority/precedence of configs
- What settings are available
- Default values

---

### Section C: Error Handling

**Q11:** What happens when a user enters an invalid command? Walk me through the code path.

**What I'm looking for:**
- exec() fails in child
- Child prints error message
- Child exits with code 127
- Parent detects failure and continues

---

**Q12:** What happens when a user presses Ctrl+C while a command is running? What about at an empty prompt?

**What I'm looking for:**
- SIGINT signal sent to foreground process group
- Child receives signal and terminates
- Parent's signal handler prevents parent termination
- Different handling at prompt vs during execution

---

**Q13:** What happens if the user enters a very long command (1000+ characters)?

**What I'm looking for:**
- Buffer limitations (if any)
- Graceful handling or error message
- No buffer overflow vulnerabilities

---

### Section D: Testing and Validation

**Q14:** How did you test your shell? What testing framework did you use?

**What I'm looking for:**
- Unit tests (pytest)
- Integration tests
- Manual testing
- Test coverage metrics

---

**Q15:** What is your test coverage percentage? Which parts of the code are NOT covered by tests?

**What I'm looking for:**
- Actual percentage (goal: 90%+)
- Understanding of what's not covered
- Justification for uncovered code (if any)

---

**Q16:** Did you test on different Linux distributions? What about different shells (bash, zsh, sh)?

**What I'm looking for:**
- POSIX compliance testing
- Portability considerations
- Testing on Ubuntu (minimum requirement)

---

### Section E: Architecture and Design

**Q17:** Why did you choose Python over C for this assignment? What are the tradeoffs?

**What I'm looking for:**
- Understanding of assignment flexibility
- POSIX system calls still used via os module
- Tradeoffs: easier development vs potential performance
- Knowledge that core concepts (fork/exec/wait) are the same

---

**Q18:** Explain your project structure. Why is the code organized this way?

**What I'm looking for:**
- Separation of concerns
- Modular design (parser, executor, builtins separate)
- Testability
- Maintainability

---

**Q19:** If you had to add job control (background processes with `&`), how would you modify your design?

**What I'm looking for:**
- Understanding of background vs foreground
- No waiting for background processes
- Process tracking/management
- Job control signals

---

**Q20:** What security considerations did you implement?

**What I'm looking for:**
- Input validation
- No shell injection vulnerabilities
- Proper handling of special characters
- Use of execvp (vs system()) to avoid shell injection

---

## Code Review Checklist

### General Code Quality

- [ ] Code is well-formatted and follows consistent style
- [ ] Variable and function names are descriptive
- [ ] No magic numbers (constants are named)
- [ ] No code duplication (DRY principle)
- [ ] No commented-out code blocks
- [ ] No debug print statements left in production code

### Documentation

- [ ] Every function has a docstring
- [ ] Docstrings include parameters, return values, and examples
- [ ] Complex algorithms have explanatory comments
- [ ] System call usage is documented with references
- [ ] Edge cases are documented

### Error Handling

- [ ] All system calls check return values
- [ ] fork() failure is handled
- [ ] exec() failure is handled
- [ ] wait() errors are handled
- [ ] File I/O errors are handled (config loading)
- [ ] User input errors are handled gracefully
- [ ] Errors go to stderr, not stdout

### Process Management

- [ ] fork() is called correctly
- [ ] Child process calls exec() family function
- [ ] Parent process calls wait() or waitpid()
- [ ] Exit status is extracted correctly
- [ ] No zombie processes created
- [ ] Child process handles exec() failure properly
- [ ] Signal handlers are set up correctly

### Parsing

- [ ] Quoted arguments are handled correctly
- [ ] Empty input is handled
- [ ] Whitespace-only input is handled
- [ ] Unclosed quotes are handled
- [ ] Wildcard expansion works (if implemented)
- [ ] Special characters are escaped properly

### Built-in Commands

- [ ] Built-in commands run in parent process (no fork)
- [ ] `exit` command works
- [ ] `cd` command works
- [ ] `pwd` command works
- [ ] `help` command works (if implemented)
- [ ] Built-in errors are handled

### Configuration

- [ ] Configuration files load correctly
- [ ] Missing config files use defaults (no crash)
- [ ] Invalid YAML is handled gracefully
- [ ] Configuration precedence is correct
- [ ] Paths are expanded (~, environment variables)

### Testing

- [ ] Unit tests exist for all modules
- [ ] Integration tests exist
- [ ] Tests cover edge cases
- [ ] Tests cover error conditions
- [ ] Test coverage is measured
- [ ] All tests pass
- [ ] Bash tests pass (if provided)

---

## Testing Scenarios

### Test Suite 1: Basic Functionality

```bash
# Test 1.1: Shell starts
akujobip1
# Expected: Prompt appears

# Test 1.2: Simple command
AkujobiP1> ls
# Expected: Directory listing

# Test 1.3: Command with one argument
AkujobiP1> ls -l
# Expected: Long format listing

# Test 1.4: Command with two arguments
AkujobiP1> cp /tmp/a.txt /tmp/b.txt
# Expected: File copied

# Test 1.5: Exit command
AkujobiP1> exit
# Expected: "Bye!" and shell terminates
```

---

### Test Suite 2: Argument Handling

```bash
# Test 2.1: No arguments
AkujobiP1> pwd
# Expected: Current directory

# Test 2.2: Single argument
AkujobiP1> echo hello
# Expected: hello

# Test 2.3: Multiple arguments
AkujobiP1> echo one two three four five
# Expected: one two three four five

# Test 2.4: Quoted argument with spaces
AkujobiP1> echo "hello world"
# Expected: hello world

# Test 2.5: Mixed quotes
AkujobiP1> echo "double" 'single' normal
# Expected: double single normal
```

---

### Test Suite 3: Error Conditions

```bash
# Test 3.1: Command not found
AkujobiP1> invalidcommand123
# Expected: Error message, shell continues

# Test 3.2: Permission denied
AkujobiP1> /etc/shadow
# Expected: Permission denied error

# Test 3.3: Empty input
AkujobiP1>
# Expected: New prompt appears

# Test 3.4: Whitespace only
AkujobiP1>
# Expected: New prompt appears

# Test 3.5: Unclosed quote
AkujobiP1> echo "unclosed
# Expected: Error message or continuation prompt
```

---

### Test Suite 4: Built-in Commands

```bash
# Test 4.1: pwd command
AkujobiP1> pwd
# Expected: /home/user/... (current directory)

# Test 4.2: cd to directory
AkujobiP1> cd /tmp
AkujobiP1> pwd
# Expected: /tmp

# Test 4.3: cd to home
AkujobiP1> cd
AkujobiP1> pwd
# Expected: /home/user

# Test 4.4: cd to previous directory
AkujobiP1> cd /tmp
AkujobiP1> cd /var
AkujobiP1> cd -
AkujobiP1> pwd
# Expected: /tmp

# Test 4.5: help command
AkujobiP1> help
# Expected: List of built-in commands
```

---

### Test Suite 5: Signal Handling

```bash
# Test 5.1: Ctrl+C during command
AkujobiP1> sleep 10
^C
AkujobiP1> echo "still alive"
# Expected: Command interrupted, shell continues

# Test 5.2: Ctrl+C at prompt
AkujobiP1> ^C
AkujobiP1>
# Expected: New prompt appears

# Test 5.3: Ctrl+D (EOF)
AkujobiP1> <Ctrl+D>
# Expected: Shell exits gracefully
```

---

### Test Suite 6: Wildcards (if implemented)

```bash
# Test 6.1: Asterisk wildcard
AkujobiP1> ls *.py
# Expected: All .py files

# Test 6.2: Question mark wildcard
AkujobiP1> ls file?.txt
# Expected: file1.txt, file2.txt, etc.

# Test 6.3: No matches
AkujobiP1> ls *.nonexistent
# Expected: No matches or literal string

# Test 6.4: Multiple wildcards
AkujobiP1> cp *.txt *.md /tmp/
# Expected: All .txt and .md files copied
```

---

### Test Suite 7: Process Management

```bash
# Test 7.1: Parent waits for child
AkujobiP1> sleep 3
# Expected: 3-second delay before prompt returns

# Test 7.2: Multiple commands in sequence
AkujobiP1> echo "first"
AkujobiP1> echo "second"
AkujobiP1> echo "third"
# Expected: All execute in order

# Test 7.3: Long-running command
AkujobiP1> sleep 30
# (wait 30 seconds)
# Expected: Prompt returns after 30 seconds

# Test 7.4: Check for zombie processes
# (in another terminal during shell execution)
ps aux | grep defunct
# Expected: No defunct/zombie processes
```

---

### Test Suite 8: Configuration

```bash
# Test 8.1: Custom config file
export AKUJOBIP1_CONFIG=/path/to/custom.yaml
akujobip1
# Expected: Custom config loaded

# Test 8.2: Local config file
cd /tmp
echo "prompt: 'CustomPrompt> '" > akujobip1.yaml
akujobip1
# Expected: CustomPrompt> appears

# Test 8.3: Missing config file
rm -f akujobip1.yaml
rm -f ~/.config/akujobip1/config.yaml
akujobip1
# Expected: Default config used, no error

# Test 8.4: Invalid YAML
echo "invalid: yaml: syntax:" > akujobip1.yaml
akujobip1
# Expected: Error message, falls back to defaults
```

---

## Grading Rubric (Detailed)

### Documentation (20 points)

**Report Content (15 points):**
- [ ] **Introduction (2 pts):** Clear project description and objectives
- [ ] **Architecture (4 pts):** Component diagram, clear explanation of modules
- [ ] **System Call Flow (4 pts):** Sequence diagram showing fork/exec/wait
- [ ] **Code Walkthrough (3 pts):** Detailed explanation of key code sections
- [ ] **Screenshots (2 pts):** At least 5 screenshots showing various features

**Code Comments (5 points):**
- [ ] **Docstrings (3 pts):** All functions have complete docstrings
- [ ] **Inline Comments (2 pts):** Complex logic is commented

**Deductions:**
- Missing sections: -2 pts each
- Poor formatting: -1 to -3 pts
- Spelling/grammar errors: -1 pt
- No diagrams: -4 pts
- Incomplete explanations: -2 pts per section

---

### Compilation (15 points)

**Installation (10 points):**
- [ ] **Dependency Installation (3 pts):** `pip install -e .` works without errors
- [ ] **No Warnings (3 pts):** No warnings during installation
- [ ] **Command Available (4 pts):** `akujobip1` command is available after install

**Runtime (5 points):**
- [ ] **Shell Starts (3 pts):** Shell starts without errors
- [ ] **No Crashes (2 pts):** Shell doesn't crash during normal operation

**Deductions:**
- Installation errors: -5 pts
- Installation warnings: -2 pts
- Command not available: -4 pts
- Runtime errors: -3 pts
- Crashes: -5 pts

---

### Correctness (60 points)

**Core Functionality (40 points):**

- [ ] **Prompt Display (5 pts):** Correct prompt format (`AkujobiP1> `)
  - Wrong format: -3 pts
  - Missing entirely: -5 pts

- [ ] **Command Execution (10 pts):** Commands execute correctly
  - Simple commands work (ls, pwd): 3 pts
  - Commands with 1 arg work: 2 pts
  - Commands with 2 args work: 2 pts
  - Commands with 3+ args work: 3 pts
  - Deduction for each failing scenario: -2 pts

- [ ] **Exit Command (5 pts):** `exit` terminates shell with message
  - Doesn't exit: -5 pts
  - No message: -2 pts
  - Wrong message: -1 pt

- [ ] **Process Management (10 pts):** Proper fork/exec/wait usage
  - fork() used correctly: 3 pts
  - exec() used correctly: 3 pts
  - wait() used correctly: 4 pts
  - Zombie processes created: -4 pts

- [ ] **Argument Parsing (5 pts):** Handles various argument formats
  - Quoted args work: 3 pts
  - Multiple args work: 2 pts
  - Parsing errors: -2 pts

- [ ] **Continuation (5 pts):** Shell continues after each command
  - Doesn't continue: -5 pts
  - Intermittent failures: -2 pts

**Error Handling (10 points):**

- [ ] **Command Not Found (4 pts):** Proper handling and error message
  - Shell crashes: -4 pts
  - No error message: -2 pts
  - Wrong exit code: -1 pt

- [ ] **Permission Errors (3 pts):** Handles unexecutable files
  - Crashes: -3 pts
  - No error handling: -2 pts

- [ ] **Input Errors (3 pts):** Handles empty input, whitespace, invalid quotes
  - Crashes on edge cases: -3 pts
  - Poor handling: -1 pt

**Advanced Features (10 points):**

- [ ] **Built-in Commands (4 pts):** cd, pwd, help work correctly
  - Each broken built-in: -1 pt
  - Built-ins fork unnecessarily: -2 pts

- [ ] **Signal Handling (3 pts):** Ctrl+C handled correctly
  - Shell exits on Ctrl+C: -3 pts
  - Child not interrupted: -2 pts

- [ ] **Configuration (3 pts):** Config system works
  - Config not loaded: -3 pts
  - Partial implementation: -1 to -2 pts

**Deductions for Major Issues:**
- Doesn't use fork(): -20 pts (core requirement)
- Doesn't use exec(): -20 pts (core requirement)
- Doesn't wait for child: -15 pts (creates zombies)
- Hardcoded command list instead of dynamic execution: -10 pts
- Uses system() instead of exec(): -15 pts (violates requirements)

---

### Readability & Misc (5 points)

**Code Quality (3 points):**
- [ ] **Well-commented (2 pts):** Adequate comments throughout code
- [ ] **Readable (1 pt):** Good variable names, formatting, structure

**Submission Format (2 points):**
- [ ] **Correct Filename (1 pt):** `CSC456_ProAssgn1_Akujobi.zip`
- [ ] **Complete Files (1 pt):** All necessary files included

**Deductions:**
- Poor commenting: -1 to -2 pts
- Unreadable code: -1 pt
- Wrong filename: -1 pt
- Missing files: -1 pt
- Unnecessary files (huge binaries, etc.): -1 pt

---

### Bonus Points (up to +5 points)

- [ ] **Exceptional Documentation (+2 pts):** Professional-quality diagrams, comprehensive report
- [ ] **Advanced Features (+3 pts):** Job control, command history, tab completion, etc.
- [ ] **Outstanding Code Quality (+2 pts):** Exemplary code organization and testing
- [ ] **Creative Enhancements (+2 pts):** Useful features beyond requirements

**Total Possible: 100 points (+5 bonus)**

---

## Edge Cases & Stress Testing

### Edge Case 1: Empty and Whitespace Input

```bash
# Empty input (just Enter)
AkujobiP1>
AkujobiP1>

# Whitespace only
AkujobiP1>
AkujobiP1>

# Tabs and spaces
AkujobiP1>
AkujobiP1>
```

**Expected:** Shell shows new prompt without errors

---

### Edge Case 2: Very Long Input

```bash
# 1000+ character command
AkujobiP1> echo aaaaaaaaaaaaaaa... (1000+ characters)
```

**Expected:** Either executes or shows reasonable error

---

### Edge Case 3: Special Characters

```bash
AkujobiP1> echo $HOME
AkujobiP1> echo `date`
AkujobiP1> echo $(whoami)
AkujobiP1> echo ~
AkujobiP1> echo *
AkujobiP1> echo ?
AkujobiP1> echo [abc]
```

**Expected:** Proper handling (expansion or literal, consistently)

---

### Edge Case 4: Unclosed Quotes

```bash
AkujobiP1> echo "unclosed quote
AkujobiP1> echo 'unclosed single
```

**Expected:** Error message or continuation prompt, no crash

---

### Edge Case 5: Nested Quotes

```bash
AkujobiP1> echo "outer 'inner' outer"
AkujobiP1> echo 'outer "inner" outer'
```

**Expected:** Proper handling of nested quotes

---

### Edge Case 6: Absolute Paths

```bash
AkujobiP1> /bin/ls
AkujobiP1> /usr/bin/python3 --version
AkujobiP1> ./local_script.sh
```

**Expected:** Commands execute even without PATH search

---

### Edge Case 7: Permission Denied

```bash
AkujobiP1> /etc/shadow
AkujobiP1> /root/.bashrc
```

**Expected:** Permission denied error, shell continues

---

### Edge Case 8: Directory as Command

```bash
AkujobiP1> /tmp
AkujobiP1> .
```

**Expected:** Error (cannot execute directory)

---

### Edge Case 9: Ctrl+D (EOF) Handling

```bash
AkujobiP1> <Ctrl+D>
```

**Expected:** Shell exits gracefully (alternative to `exit` command)

---

### Edge Case 10: Rapid Ctrl+C

```bash
AkujobiP1> sleep 100
^C^C^C^C^C
```

**Expected:** Command interrupted, shell continues, no corruption

---

### Stress Test 1: Memory Leak Detection

```bash
# Run 1000 commands and check memory usage
for i in {1..1000}; do
  echo "echo $i" | akujobip1
done

# Check memory with top or ps
```

**Expected:** No significant memory growth

---

### Stress Test 2: Zombie Process Check

```bash
# In one terminal: run shell
akujobip1

# Execute many commands
AkujobiP1> ls
AkujobiP1> pwd
AkujobiP1> date
... (repeat 100 times)

# In another terminal: check for zombies
ps aux | grep defunct
```

**Expected:** No defunct/zombie processes

---

### Stress Test 3: Concurrent Execution

```bash
# Run multiple instances of the shell
akujobip1 &
akujobip1 &
akujobip1 &
```

**Expected:** No conflicts, each instance independent

---

### Stress Test 4: Large File Wildcards

```bash
# Create 1000 files
cd /tmp/testdir
touch file{1..1000}.txt

# Try to match all
AkujobiP1> ls *.txt
```

**Expected:** All files listed (or reasonable limitation with error)

---

## Documentation Review

### Report Structure Review

**Required Sections:**

1. **Title Page**
   - [ ] Assignment title
   - [ ] Course number
   - [ ] Student name
   - [ ] Date

2. **Table of Contents** (recommended)
   - [ ] Sections numbered
   - [ ] Page numbers

3. **Introduction**
   - [ ] Project objectives stated
   - [ ] Brief overview of implementation
   - [ ] Technologies used

4. **Architecture**
   - [ ] Component diagram present
   - [ ] Clear explanation of each module
   - [ ] Data flow between components

5. **System Call Flow**
   - [ ] Sequence diagram showing fork/exec/wait
   - [ ] Detailed explanation of process lifecycle
   - [ ] Reference to POSIX standards

6. **Code Walkthrough**
   - [ ] Main loop explanation with code snippets
   - [ ] Parser explanation
   - [ ] Executor explanation
   - [ ] Built-in dispatcher explanation
   - [ ] Error handling explanation

7. **Configuration System** (if implemented)
   - [ ] Configuration file format
   - [ ] Loading precedence
   - [ ] Available settings

8. **Screenshots**
   - [ ] Shell startup
   - [ ] Simple commands
   - [ ] Commands with arguments
   - [ ] Error handling
   - [ ] Exit command
   - [ ] Built-in commands
   - [ ] Signal handling (Ctrl+C)

9. **How to Run**
   - [ ] System requirements
   - [ ] Installation steps
   - [ ] Running the shell
   - [ ] Running tests

10. **Testing**
    - [ ] Testing approach
    - [ ] Test coverage
    - [ ] Test results

11. **Conclusion**
    - [ ] Summary of implementation
    - [ ] Challenges faced
    - [ ] Lessons learned

12. **References**
    - [ ] POSIX standard references
    - [ ] man page references
    - [ ] Other resources

---

### Code Documentation Review

**File Headers:**
- [ ] Every source file has a header comment
- [ ] Header includes file purpose, author, date

**Function Documentation:**
- [ ] Every function has a docstring
- [ ] Docstring includes:
  - Purpose/description
  - Parameters (with types)
  - Return value (with type)
  - Example usage (for complex functions)
  - Exceptions raised (if any)

**Inline Comments:**
- [ ] Complex algorithms explained
- [ ] System calls documented with man page references
- [ ] Edge cases documented
- [ ] TODO items marked (if any)

**README File:**
- [ ] Installation instructions
- [ ] Usage instructions
- [ ] Configuration instructions
- [ ] Testing instructions
- [ ] Project structure overview

---

## Final Assessment Questions

### Question Set 1: Understanding (Oral Exam)

**Q1:** Without looking at your code, explain to me step-by-step what happens when I type `ls -la` in your shell and press Enter. Include every system call.

**Q2:** What is the purpose of the `fork()` system call? What does it return in the parent process? What does it return in the child process?

**Q3:** Why do we need to call `wait()` after forking a child process? What happens if we don't?

**Q4:** Explain the difference between `exit()` in your built-in commands and `exit()` in a child process after `exec()` fails.

**Q5:** How would you modify your shell to support pipes (e.g., `ls | grep txt`)? What system calls would you need?

---

### Question Set 2: Debugging Scenarios

**Scenario 1:** "When I run your shell and execute commands, I notice that `ps aux` shows many defunct processes. What's wrong and how would you fix it?"

**Expected Answer:** Not calling wait(), need to add waitpid() in executor

---

**Scenario 2:** "When I type `cd /tmp` in your shell, it doesn't change the directory. Why?"

**Expected Answer:** cd is being executed in child process instead of parent, need to make cd a built-in

---

**Scenario 3:** "When I press Ctrl+C in your shell, the entire shell exits. How can you fix this?"

**Expected Answer:** Need to set up SIGINT signal handler to ignore or handle gracefully

---

**Scenario 4:** "When I run a command that doesn't exist, your shell crashes. What's the problem?"

**Expected Answer:** exec() fails but child process continues executing shell code, need to check exec() return and exit child

---

**Scenario 5:** "I typed `echo 'hello world'` but your shell printed `'hello world'` with the quotes. What's wrong?"

**Expected Answer:** Not using proper parser (like shlex) that strips quotes

---

### Question Set 3: Extension Scenarios

**Scenario 1:** "How would you add support for background processes using `&`?"

**What I'm looking for:**
- Don't wait for background processes
- Track background PIDs
- Handle SIGCHLD signal
- Reap zombies asynchronously

---

**Scenario 2:** "How would you implement command history (up arrow to recall previous commands)?"

**What I'm looking for:**
- Store commands in a list/file
- Use readline library or custom input handler
- Arrow key handling

---

**Scenario 3:** "How would you add support for environment variable expansion like `echo $HOME`?"

**What I'm looking for:**
- Parse input for $ symbols
- Look up in os.environ
- Replace before execution
- Handle undefined variables

---

**Scenario 4:** "How would you implement redirection like `ls > output.txt`?"

**What I'm looking for:**
- Parse for > or <
- Open file in child process
- Use dup2() to redirect stdout/stdin
- Close original file descriptor

---

## Evaluation Summary

### Quick Pass/Fail Criteria

**Automatic Fail (0-40 points):**
- Doesn't use fork() at all
- Doesn't use exec() at all
- Shell crashes on basic commands
- Cannot compile/run

**Minimal Pass (40-60 points):**
- Basic functionality works
- Major bugs or missing features
- Poor documentation
- Minimal error handling

**Satisfactory (60-75 points):**
- All basic requirements met
- Some bugs or missing edge cases
- Adequate documentation
- Basic error handling

**Good (75-85 points):**
- All requirements met
- Handles most edge cases
- Good documentation
- Good error handling
- Clean code

**Excellent (85-95 points):**
- All requirements exceeded
- Handles all edge cases
- Excellent documentation
- Robust error handling
- Exemplary code quality

**Outstanding (95-100+ points):**
- Professional-quality implementation
- Advanced features
- Comprehensive testing
- Publication-quality documentation
- Creative enhancements

---

## Final Notes

As your professor, I will be thorough in my evaluation. I will test not only the happy path but also edge cases and error conditions. I expect you to:

1. **Understand your code deeply** - Be able to explain every line
2. **Know the system calls** - Understand fork, exec, wait at the system level
3. **Handle errors gracefully** - No crashes, proper error messages
4. **Document thoroughly** - Code comments and written report
5. **Test comprehensively** - Show me your test suite and results

**Remember:** This assignment is about process management, not shell features. Focus on correct implementation of fork(), exec(), and wait() before adding advanced features.

**Good luck!**

---

**Document Version:** 1.0
**Date:** 2025-11-09
**Prepared by:** Course Instructor (Professor's Perspective)
**For:** CSC456 Programming Assignment 1 Review
