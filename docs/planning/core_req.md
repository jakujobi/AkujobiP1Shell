# 1. Objectives

- Demonstrate the process management
- Implement process management using system calls

# 2. Overview

Implement a simple shell (a command-line interpreter), which can read user's commands (i.e., any Linux/Unix commands such as ls, cp, mkdir, . . . ) from Standard Input and execute commands using the system calls related to process management.

# 3. Requirements

Your shell must display a prompt consisting of your last name, for example,

```
AkujobiP1>
```

Your shell must read a user command and its argument(s). Your shell must be able to take any number of arguments, for example,

```
AkujobiP1>ls -l
AkujobiP1>cp fileA fileB
```

In the first example, there is only one argument, '-l', and in the second example, there are two arguments, which are 'fileA' and 'fileB'.

Note that your program will be evaluated with random commands with one, two, and three arguments.

Your shell must continue to take another user command after completing the execution of the previous command, for example,

```
AkujobiP1e>ls
... fileA.txt fileB.txt
Your last name>
```

When a user types 'exit,' your shell must terminate, for example,

```
Your last name>exit
Bye!
```

Your shell (a parent process) must wait until its child process (a user command) finishes its execution.

To run a user command, consider using the system call 'exec()'. Read the manual of this system call (e.g., https://man7.org/linux/man-pages/man3/exec.3.html). You will find that there are different ways of using this system call. It is your task to read the manual and select an appropriate one for this programming assignment. For example, your exec() system call is used to execute a program with an arbitrary number of arguments.

Your shell must run on a POSIX-compliant operating system.

# 4. Project Management Tool

Select a project management tool of your preference, e.g., SVN, Git, etc.

Read the manual of your preferred project management tool.

Be prepared! You will use a project management tool for the following programming assignment.

# 5. What to turn in?

Submit a zip file (filename: CSC456 ProAssgn1 Your name.zip) that is expected to include the following files:

- Your source and header (if any) files (e.g., 'c' or 'cpp', and 'h' files)
- A makefile (if any)
- All other supplemental files that are needed to run your program
- A report that describes briefly about how to run your program
- Submit your zip file to the Dropbox on D2L

# 6. Evaluation Criteria

- Documentation. 20% - your report clearly describes how to run your program and how you addressed the program requirements.
- Compilation. 15% - your code can be compiled without errors or warnings.
- Correctness. 60% - your program satisfies all the program requirements.
- Readability and Misc. 5% - your source code must be well commented. Your submitted zip file name complies with the instructions in Section 4. Your zip file contains all files that are needed to run your program
