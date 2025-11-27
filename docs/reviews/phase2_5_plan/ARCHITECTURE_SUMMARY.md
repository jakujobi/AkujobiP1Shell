# Phase 2.5 Architecture Summary

**Date:** 2025-11-10  
**Phase:** Main Shell Loop (shell.py)  
**Purpose:** Visual understanding of how the shell works

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        AkujobiP1 Shell                          │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                   cli() Entry Point                      │  │
│  │  • Load configuration                                    │  │
│  │  • Handle startup errors                                 │  │
│  │  • Call run_shell()                                      │  │
│  └──────────────┬───────────────────────────────────────────┘  │
│                 │                                               │
│                 ▼                                               │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              run_shell() Main Loop                       │  │
│  │                                                           │  │
│  │  while True:                                             │  │
│  │    1. Display prompt                                     │  │
│  │    2. Read input (handle Ctrl+C, Ctrl+D)                │  │
│  │    3. Parse command                                      │  │
│  │    4. Skip if empty                                      │  │
│  │    5. Check if built-in                                  │  │
│  │    6. Execute (built-in or external)                     │  │
│  │    7. Check for exit signal (-1)                         │  │
│  │    8. Loop                                               │  │
│  └─┬──────────┬────────────┬──────────────────────┬─────────┘  │
│    │          │            │                      │             │
│    ▼          ▼            ▼                      ▼             │
│  ┌────┐   ┌────────┐   ┌─────────┐         ┌─────────┐        │
│  │Config│  │Parser  │   │Builtins │         │Executor │        │
│  │      │  │        │   │         │         │         │        │
│  │Load  │  │Parse   │   │exit, cd,│         │Fork/    │        │
│  │YAML  │  │Quote   │   │pwd, help│         │Exec/    │        │
│  │Merge │  │Wildcard│   │         │         │Wait     │        │
│  └────┘   └────────┘   └─────────┘         └─────────┘        │
│   Phase      Phase         Phase               Phase           │
│    2.1        2.2           2.3                 2.4            │
│     SUCCESS          SUCCESS             SUCCESS                   SUCCESS             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Data Flow Diagram

```
User Input
   │
   ▼
┌──────────────────┐
│  Input prompt    │  input("AkujobiP1> ")
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  Parse command   │  parse_command(line, config)
└────────┬─────────┘
         │
         ├─── Returns []  ───►  Continue (skip empty)
         │
         ├─── Returns ['cmd', 'arg1', ...]
         │
         ▼
┌──────────────────┐
│  Check type      │  get_builtin(args[0])
└────┬────────┬────┘
     │        │
     │ None   │ BuiltinCommand
     │        │
     ▼        ▼
┌─────────┐ ┌──────────────┐
│External │ │   Built-in   │
│Command  │ │   Command    │
│         │ │              │
│Fork/    │ │Execute in    │
│Exec/    │ │shell process │
│Wait     │ │              │
└────┬────┘ └──────┬───────┘
     │             │
     │ Returns     │ Returns
     │ 0-255       │ 0, 1-125, or -1
     │             │
     └──────┬──────┘
            │
            ▼
     ┌──────────────┐
     │  Check code  │  if exit_code == -1
     └──────┬───────┘
            │
            ├─── -1  ───►  Return 0 (exit shell)
            │
            └─── Other  ───►  Continue loop
```

---

## Main Loop State Machine

```
        START
          │
          ▼
    ┌─────────┐
    │ Display │
    │ Prompt  │
    └────┬────┘
         │
         ▼
    ┌─────────┐
    │  Read   │◄──────────────┐
    │ Input   │               │
    └─┬──┬──┬─┘              │
      │  │  │                 │
      │  │  └── EOFError ──► Exit Shell
      │  │
      │  └──── KeyboardInterrupt ──► Print \n
      │                               │
      │                               │
      ▼                               │
 ┌─────────┐                         │
 │  Parse  │                         │
 │ Command │                         │
 └────┬────┘                         │
      │                               │
      ├── Empty ─────────────────────┤
      │                               │
      ▼                               │
 ┌─────────┐                         │
 │  Check  │                         │
 │Built-in?│                         │
 └──┬───┬──┘                         │
    │   │                             │
    │   └── External                  │
    │       │                         │
    │       ▼                         │
    │  ┌─────────┐                   │
    │  │ Execute │                   │
    │  │External │                   │
    │  └────┬────┘                   │
    │       │                         │
    ▼       ▼                         │
  ┌──────────┐                       │
  │ Execute  │                       │
  │Built-in  │                       │
  └────┬─────┘                       │
       │                              │
       ├── Returns -1 ──► Exit Shell │
       │                              │
       └────────────────────────────►┘
```

---

## Signal Handling Flow

### Ctrl+C During Input

```
User presses Ctrl+C
       ↓
Python receives SIGINT
       ↓
input() raises KeyboardInterrupt
       ↓
Shell catches exception
       ↓
┌────────────────┐
│  Print newline │
│  Continue loop │
│  Show prompt   │
└────────────────┘
```

### Ctrl+C During Command Execution

```
User presses Ctrl+C
       ↓
Terminal sends SIGINT to foreground process
       ↓
┌─────────────────────────────┐
│  Child process receives it  │
│  (executor reset handler)   │
└────────────┬────────────────┘
             ↓
    Child process terminates
             ↓
┌─────────────────────────────┐
│  Parent blocked in waitpid()│
│  Returns when child exits   │
└────────────┬────────────────┘
             ↓
    Continue shell loop
    Show new prompt
```

### Ctrl+D (EOF)

```
User presses Ctrl+D
       ↓
input() raises EOFError
       ↓
Shell catches exception
       ↓
┌────────────────┐
│  Print newline │
│  Print "Bye!"  │
│  Return 0      │
│  Exit shell    │
└────────────────┘
```

---

## Module Integration Map

```
┌─────────────────────────────────────────────────────────┐
│                      shell.py                           │
│                                                         │
│  cli() ─────► load_config() ─────────────┐            │
│                                            │            │
│                                            ▼            │
│  run_shell(config) ──────────────────────────────────► │
│       │                                                │
│       ├──► parse_command(line, config) ──────────────► │
│       │         Phase 2.2                   │          │
│       │                                     ▼          │
│       │                              Returns List[str] │
│       │                                     │          │
│       ├──► get_builtin(args[0]) ──────────► │         │
│       │         Phase 2.3                   │          │
│       │                                     ▼          │
│       │                          Returns BuiltinCommand│
│       │                                   or None      │
│       │                                     │          │
│       │         If BuiltinCommand:          │          │
│       ├──► builtin.execute(args, config) ──► │        │
│       │                │                      │        │
│       │                └─ Returns int (-1, 0-125)     │
│       │                                                │
│       │         If None (external):                    │
│       └──► execute_external_command(args, config) ───► │
│                   Phase 2.4                 │          │
│                                             └─ Returns int (0-255)
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## Exception Handling Hierarchy

```
run_shell()
    │
    └─ while True:
            │
            └─ try:
                │
                ├─ input(prompt)
                │    │
                │    ├─ Normal: Returns string
                │    ├─ EOFError: Exit shell
                │    └─ KeyboardInterrupt: Continue loop
                │
                ├─ parse_command()
                │    │
                │    ├─ Normal: Returns List[str]
                │    ├─ Empty: Returns []
                │    └─ Error: Returns [] (prints error)
                │
                ├─ get_builtin()
                │    │
                │    ├─ Found: Returns BuiltinCommand
                │    └─ Not found: Returns None
                │
                ├─ builtin.execute() or execute_external_command()
                │    │
                │    ├─ Returns -1: Exit shell
                │    ├─ Returns 0-125: Continue
                │    └─ Returns 126-255: Continue (external only)
                │
                └─ except Exception:
                     │
                     └─ Print error, continue loop (defensive)
```

---

## Module Readiness Status

```
┌────────────────────┬────────┬───────┬──────────┬────────────┐
│ Module             │ Status │ Tests │ Coverage │ Grade      │
├────────────────────┼────────┼───────┼──────────┼────────────┤
│ Config (Phase 2.1) │    SUCCESS   │   39  │   92%    │ A-         │
│ Parser (Phase 2.2) │    SUCCESS   │   56  │   97%    │ A          │
│ Builtins (2.3)     │    SUCCESS   │   35  │  100%    │ A+         │
│ Executor (2.4)     │    SUCCESS   │   41  │  ~95%    │ A+ (98%)   │
├────────────────────┼────────┼───────┼──────────┼────────────┤
│ Shell (Phase 2.5)  │   📋   │   50  │   95%    │ A+ (target)│
└────────────────────┴────────┴───────┴──────────┴────────────┘

Total Existing Tests: 171 passing
Target New Tests: 50
Total After Phase 2.5: 221 tests
```

---

## Configuration Flow

```
Startup
   │
   ▼
load_config()
   │
   ├─── Check $AKUJOBIP1_CONFIG ──────► File exists?
   │                                    │
   │                                    ├─ Yes: Load YAML
   │                                    └─ No: Continue
   │
   ├─── Check ./akujobip1.yaml ───────► File exists?
   │                                    │
   │                                    ├─ Yes: Load YAML
   │                                    └─ No: Continue
   │
   ├─── Check ~/.config/akujobip1/config.yaml
   │                                    │
   │                                    ├─ Yes: Load YAML
   │                                    └─ No: Continue
   │
   └─── Use built-in defaults
   
Result: Dict[str, Any]
   │
   └─► Pass to run_shell(config)
           │
           ├─► Pass to parse_command(line, config)
           ├─► Pass to builtin.execute(args, config)
           └─► Pass to execute_external_command(args, config)
```

---

## Command Execution Paths

### Path 1: Built-in Command (exit)

```
User types: "exit"
     │
     ▼
input() returns "exit"
     │
     ▼
parse_command("exit", config)
     │
     ▼
Returns ['exit']
     │
     ▼
get_builtin('exit')
     │
     ▼
Returns ExitCommand instance
     │
     ▼
ExitCommand.execute(['exit'], config)
     │
     ├─ Prints "Bye!"
     └─ Returns -1
           │
           ▼
     Shell checks: if exit_code == -1
           │
           ▼
     return 0
           │
           ▼
     SHELL EXITS
```

### Path 2: Built-in Command (cd)

```
User types: "cd /tmp"
     │
     ▼
parse_command("cd /tmp", config)
     │
     ▼
Returns ['cd', '/tmp']
     │
     ▼
get_builtin('cd')
     │
     ▼
Returns CdCommand instance
     │
     ▼
CdCommand.execute(['cd', '/tmp'], config)
     │
     ├─ Calls os.chdir('/tmp')
     └─ Returns 0
           │
           ▼
     Shell continues loop
```

### Path 3: External Command

```
User types: "ls -la"
     │
     ▼
parse_command("ls -la", config)
     │
     ▼
Returns ['ls', '-la']
     │
     ▼
get_builtin('ls')
     │
     ▼
Returns None (not a built-in)
     │
     ▼
execute_external_command(['ls', '-la'], config)
     │
     ├─ Forks process
     ├─ Child: execvp('ls', ['ls', '-la'])
     └─ Parent: waitpid()
           │
           ▼
     Returns exit code (0)
           │
           ▼
     Shell continues loop
```

### Path 4: Empty Input

```
User presses Enter
     │
     ▼
input() returns ""
     │
     ▼
parse_command("", config)
     │
     ▼
Returns []
     │
     ▼
Shell checks: if not args
     │
     ▼
continue
     │
     ▼
Show prompt again
```

---

## Error Recovery Paths

### Parse Error

```
User types: echo "unclosed
     │
     ▼
parse_command('echo "unclosed', config)
     │
     ├─ shlex raises ValueError
     ├─ Prints "Parse error: ..."
     └─ Returns []
           │
           ▼
     Shell checks: if not args
           │
           ▼
     continue (show prompt again)
```

### Command Not Found

```
User types: notacommand
     │
     ▼
execute_external_command(['notacommand'], config)
     │
     ├─ Fork succeeds
     ├─ Child: execvp raises FileNotFoundError
     ├─ Child: Prints "notacommand: command not found"
     ├─ Child: os._exit(127)
     └─ Parent: waitpid returns status
           │
           ▼
     Returns 127
           │
           ▼
     Shell continues loop
```

### Unexpected Error

```
Something unexpected happens
     │
     ▼
Exception raised in main loop
     │
     ▼
except Exception as e:
     │
     ├─ Prints "Shell error: ..."
     ├─ Optionally prints traceback
     └─ continue
           │
           ▼
     Show prompt again
     Shell keeps running
```

---

## Testing Strategy Map

```
┌─────────────────────────────────────────────────────────┐
│                    Test Coverage                        │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Basic Functionality (8 tests)                         │
│  ├─ Prompt display                                     │
│  ├─ Empty input                                        │
│  ├─ Command execution                                  │
│  └─ Exit behavior                                      │
│                                                         │
│  Built-in Integration (8 tests)                        │
│  ├─ exit command                                       │
│  ├─ cd command                                         │
│  ├─ pwd command                                        │
│  └─ help command                                       │
│                                                         │
│  External Integration (8 tests)                        │
│  ├─ Command execution                                  │
│  ├─ Command not found                                  │
│  ├─ Permission denied                                  │
│  └─ Exit codes                                         │
│                                                         │
│  Signal Handling (6 tests)                             │
│  ├─ Ctrl+C during input                                │
│  ├─ Ctrl+C during command                              │
│  ├─ Ctrl+D                                             │
│  └─ Multiple signals                                   │
│                                                         │
│  Error Handling (5 tests)                              │
│  ├─ Parse errors                                       │
│  ├─ Built-in errors                                    │
│  ├─ Executor errors                                    │
│  └─ Unexpected errors                                  │
│                                                         │
│  Edge Cases (5 tests)                                  │
│  ├─ Very long input                                    │
│  ├─ Multiple commands                                  │
│  ├─ Whitespace handling                                │
│  └─ Special characters                                 │
│                                                         │
│  Configuration (5 tests)                               │
│  ├─ Custom prompt                                      │
│  ├─ Custom exit message                                │
│  ├─ Missing keys                                       │
│  └─ Invalid config                                     │
│                                                         │
│  Bash Test Simulation (5 tests)                        │
│  ├─ Test 1: exit                                       │
│  ├─ Test 2: empty then exit                            │
│  ├─ Test 3: unknown command                            │
│  └─ Test 4: quoted args                                │
│                                                         │
├─────────────────────────────────────────────────────────┤
│  Total: 50 tests                                        │
│  Target Coverage: 95%+                                  │
│  Expected Grade: A+ (98/100)                            │
└─────────────────────────────────────────────────────────┘
```

---

## Implementation Complexity Analysis

```
Function: cli()
├─ Complexity: LOW
├─ Lines: ~15
├─ Logic: Linear (no branches)
└─ Coverage: 100% expected

Function: run_shell()
├─ Complexity: MEDIUM
├─ Lines: ~60
├─ Logic: Loop with multiple branches
├─ Coverage: 95%+ expected
└─ Critical paths:
    ├─ Normal execution
    ├─ EOFError handling
    ├─ KeyboardInterrupt handling
    ├─ Empty input handling
    ├─ Exit code -1 handling
    └─ Exception handling

Total Lines: ~150 (well under 300 limit)
Cyclomatic Complexity: <10 per function
```

---

## Success Indicators

```
 SUCCESS All module interfaces understood
 SUCCESS Critical issues identified and mitigated
 SUCCESS Signal handling approach decided (no custom handler)
 SUCCESS Exit code handling planned (check for -1)
 SUCCESS Empty args handling planned (check before index)
 SUCCESS Config safety planned (use .get())
 SUCCESS Exception handling planned (defensive)
 SUCCESS Test strategy comprehensive (50 tests)
 SUCCESS Bash tests understood and will be simulated
 SUCCESS Implementation time estimated (3-4 hours)
 SUCCESS Expected grade: A+ (98/100)

🚀 READY TO IMPLEMENT
```

---

**This architecture document provides:**
- Visual understanding of system components
- Clear data flow paths
- Signal handling clarity
- Module integration map
- Error recovery strategies
- Testing approach
- Implementation complexity analysis

**Next step:** Start implementation following the plan!

