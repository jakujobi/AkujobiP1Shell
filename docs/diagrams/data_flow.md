# Data Flow Diagram

This diagram shows the flow of data and control through the shell from user input to command execution.

```mermaid
flowchart TD
    Start(["User Starts Shell"]) --> LoadConfig["Load Configuration<br/>config.py"]
    LoadConfig --> ShowPrompt["Display Prompt<br/>AkujobiP1>"]
    
    ShowPrompt --> ReadInput["Read User Input<br/>input()"]
    
    ReadInput --> CheckEmpty{"Input<br/>Empty?"}
    CheckEmpty -->|"Yes"| ShowPrompt
    CheckEmpty -->|"No"| ParseCommand["Parse Command<br/>parser.py"]
    
    ParseCommand --> Tokenize["Tokenize with shlex<br/>Handle quotes"]
    Tokenize --> CheckWildcard{"Wildcards<br/>Enabled?"}
    
    CheckWildcard -->|"Yes"| ExpandGlob["Expand Wildcards<br/>glob.glob"]
    CheckWildcard -->|"No"| CheckArgs
    ExpandGlob --> CheckArgs{"Args<br/>Valid?"}
    
    CheckArgs -->|"No"| ShowError1["Print Parse Error"]
    ShowError1 --> ShowPrompt
    CheckArgs -->|"Yes"| CheckBuiltin{"Is<br/>Built-in?"}
    
    CheckBuiltin -->|"Yes"| ExecuteBuiltin["Execute Built-in<br/>builtins.py"]
    CheckBuiltin -->|"No"| ExecuteExternal["Execute External<br/>executor.py"]
    
    ExecuteBuiltin --> CheckExit{"Exit<br/>Code = -1?"}
    CheckExit -->|"Yes"| ExitShell["Print Exit Message<br/>Terminate Shell"]
    CheckExit -->|"No"| ShowPrompt
    
    ExecuteExternal --> Fork["Fork Process<br/>os.fork"]
    Fork --> ForkDecision{"Parent<br/>or Child?"}
    
    ForkDecision -->|"Child"| ResetSignals["Reset Signal Handlers<br/>signal.SIG_DFL"]
    ResetSignals --> Execvp["Execute Command<br/>os.execvp"]
    Execvp --> ExecSuccess{"Exec<br/>Success?"}
    
    ExecSuccess -->|"Yes"| ReplaceProcess["Process Replaced<br/>No Return"]
    ExecSuccess -->|"No"| ExecError{"Error<br/>Type?"}
    
    ExecError -->|"Not Found"| Exit127["Print Error<br/>os._exit 127"]
    ExecError -->|"No Permission"| Exit126["Print Error<br/>os._exit 126"]
    ExecError -->|"Other"| Exit1["Print Error<br/>os._exit 1"]
    
    ForkDecision -->|"Parent"| WaitChild["Wait for Child<br/>os.waitpid"]
    WaitChild --> ExtractStatus["Extract Exit Status<br/>WIFEXITED WEXITSTATUS"]
    
    ExtractStatus --> CheckShowExit{"Show<br/>Exit Codes?"}
    CheckShowExit -->|"Never"| ShowPrompt
    CheckShowExit -->|"On Failure"| CheckCode{"Exit<br/>Code != 0?"}
    CheckShowExit -->|"Always"| DisplayExit["Display Exit Code<br/>Exit: N"]
    
    CheckCode -->|"Yes"| DisplayExit
    CheckCode -->|"No"| ShowPrompt
    DisplayExit --> ShowPrompt
    
    ExitShell --> End(["Shell Exits"])
    
    %% Signal Handling
    ReadInput -.->|"Ctrl+D"| EOFCaught["Catch EOFError"]
    ReadInput -.->|"Ctrl+C"| InterruptCaught["Catch KeyboardInterrupt"]
    EOFCaught --> ExitShell
    InterruptCaught --> NewLine["Print Newline"]
    NewLine --> ShowPrompt
    
    %% Error Handling
    ParseCommand -.->|"Parse Error"| ShowError2["Print Error Message"]
    ShowError2 --> ShowPrompt
    
    ExecuteBuiltin -.->|"Exception"| CatchError["Catch Exception<br/>Print Error"]
    ExecuteExternal -.->|"Exception"| CatchError
    CatchError --> CheckVerbose{"Verbose<br/>Errors?"}
    CheckVerbose -->|"Yes"| ShowTraceback["Print Traceback"]
    CheckVerbose -->|"No"| ShowPrompt
    ShowTraceback --> ShowPrompt
    
    style Start fill:#e8f5e9
    style End fill:#ffebee
    style ShowPrompt fill:#e1f5ff
    style LoadConfig fill:#fff3e0
    style ParseCommand fill:#f3e5f5
    style ExecuteBuiltin fill:#e8f5e9
    style ExecuteExternal fill:#ffebee
    style Fork fill:#ffe0b2
    style ExitShell fill:#ffcdd2
```

## Flow Description

### 1. Initialization Phase
1. Shell starts and loads configuration from YAML files
2. Configuration is merged with priority order
3. Default values are applied for missing settings

### 2. Main Loop (REPL)
1. **Display Prompt**: Shows configured prompt text
2. **Read Input**: Waits for user input using `input()`
3. **Empty Check**: Skips empty lines and whitespace

### 3. Parsing Phase
1. **Tokenization**: Uses `shlex.split()` to handle quotes
2. **Wildcard Expansion**: Expands `*`, `?`, `[...]` if enabled
3. **Validation**: Returns empty list on parse errors

### 4. Dispatch Phase
1. **Built-in Check**: Looks up command in built-in registry
2. **Route**: Sends to built-in handler or external executor

### 5a. Built-in Execution
1. **Direct Execution**: No forking, runs in same process
2. **Exit Detection**: Checks for return code -1 (exit command)
3. **Continue**: Returns to prompt for next command

### 5b. External Execution
1. **Fork**: Creates child process duplicate
2. **Child Path**: 
   - Resets signal handlers
   - Executes command with `execvp()`
   - Exits with error code if exec fails
3. **Parent Path**:
   - Waits for child with `waitpid()`
   - Extracts exit status with POSIX macros
   - Displays exit code based on configuration

### 6. Signal Handling
- **Ctrl+D (EOF)**: Exits shell gracefully with exit message
- **Ctrl+C (SIGINT)**: Cancels current line, shows new prompt
- **Child Signals**: Routed to child process, not parent shell

### 7. Error Handling
- **Parse Errors**: Prints error, shows new prompt
- **Execution Errors**: Catches exceptions, continues running
- **Verbose Mode**: Optionally shows full tracebacks

## Key Decision Points

### Is Built-in?
- **Yes**: Execute directly without forking (cd, pwd, help, exit)
- **No**: Use fork/exec/wait pattern for external commands

### Exit Code = -1?
- **Yes**: Exit command was executed, terminate shell
- **No**: Continue to next iteration of REPL loop

### Show Exit Codes?
- **Never**: Don't display any exit codes
- **On Failure**: Display only when exit code is non-zero
- **Always**: Display exit code for every command

## Exit Codes

Standard POSIX exit codes:
- **0**: Success
- **1-125**: Command-specific errors
- **126**: Permission denied (cannot execute)
- **127**: Command not found
- **128+N**: Terminated by signal N

---

**Created:** 2025-11-10  
**Author:** John Akujobi  
**Project:** AkujobiP1Shell - CSC456 Programming Assignment 1

