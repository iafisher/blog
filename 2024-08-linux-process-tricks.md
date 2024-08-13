# Linux process tricks
*Thank you to [Julian Squires](https://www.cipht.net/) for his assistance with this project.*

Last week I gave a demo at [Recurse Center](https://recurse.com) of the cool and strange things you can do by abusing the `ptrace` system call on Linux. I promised at the time that I'd write a blog post explaining how I did it. So here it is. It was a little more magical to demo this live, but hopefully the screen recordings I've included below give you some idea.

## Warm-up: Pausing and resuming a process
<video controls>
  <source src="https://iafisher.com/static/blog/uploads/process_magic/demo-pause-resume.avif" />
</video>

Here and throughout, `p` is the program I wrote that implements these tricks; `countforever` is a [simple C program](https://github.com/iafisher/process-magic/blob/master/examples/countforever.c) that I use as an example.

## Rewinding a process
<video controls>
  <source src="https://iafisher.com/static/blog/uploads/process_magic/demo-rewind.avif" />
</video>

## Taking over a running process
<video controls>
  <source src="https://iafisher.com/static/blog/uploads/process_magic/demo-takeover.avif" />
</video>

Notice how inside the Python interpreter, `os.getpid()` reports the same PID as the original program.

## Freezing and thawing a running process
<video controls>
  <source src="https://iafisher.com/static/blog/uploads/process_magic/demo-freeze-thaw.avif" />
</video>

## Manipulating program output
[ROT13](https://en.wikipedia.org/wiki/ROT13)-encrypting a Python interpreter session:

<video controls>
  <source src="https://iafisher.com/static/blog/uploads/process_magic/demo-rot13.avif" />
</video>

What I typed is `print("Hello, world!")`. The Python interpreter sees the original input, but the output is ROT13-encrypted before being printed to the screen.

Highlighting error output in red:

<video controls>
  <source src="https://iafisher.com/static/blog/uploads/process_magic/demo-colorize.avif" />
</video>

## How it works
These tricks use two Linux system interfaces: the [`ptrace`](https://man7.org/linux/man-pages/man2/ptrace.2.html) system call, which lets one process trace and control another, and [`procfs`](https://en.wikipedia.org/wiki/Procfs), a filesystem interface for inspecting the status of running processes. `ptrace` is what is used by debuggers like GDB, and `procfs` is how the `ps` command reads information about the processes on your system.

### Syscall injection
Many of the tricks rely on making syscalls from the traced process. Taking over a running process requires making an `execve` syscall, for instance. `ptrace` can't do this directly, so you have to do it manually:

1. Get the current registers with `PTRACE_GETREGSET`.
2. Set the appropriate register to the syscall number ([this table](https://gpages.juszkiewicz.com.pl/syscalls-table/syscalls.html) helps), and place the arguments in registers. If the argument is a pointer (e.g., to a string constant), you'll need to inject the data somewhere in the process's memory. The registers to use are architecture-specific; on ARM64, the syscall number goes in `x8`, and the arguments go in registers `x0`, `x1`, and so on.
3. Set the program counter to a syscall instruction, either by finding one already in the binary, or by injecting your own.
4. Single-step the program with `PTRACE_SINGLESTEP` to execute the syscall.
5. Get the current registers again, and read the syscall result from the return register (`x0` on ARM64).
6. Restore the original registers from step 1.

[Here's](https://github.com/iafisher/process-magic/blob/ae72fcaa8d7a3c5a149afd69a1f5eb28706ca729/src/proctool/pcontroller.rs#L122) the code. Steps 1 and 6 are omitted from that function, but can be found [elsewhere](https://github.com/iafisher/process-magic/blob/ae72fcaa8d7a3c5a149afd69a1f5eb28706ca729/src/proctool/bin/daemon.rs#L147-L172).

### Pause and resume a process
Pausing and resuming is as simple as calling `PTRACE_ATTACH` and `PTRACE_DETACH`. The one wrinkle is that the traced process will be automatically detached and restarted if the tracing process exits. So `p pause` and `p resume` call out to a long-running daemon process that keeps the `ptrace` connection alive.

### Take over a running process
I think this is the trick that people were most impressed by, but in fact it's quite simple. You just need to inject an [`execve`](https://man7.org/linux/man-pages/man2/execve.2.html) syscall and pass the path to the new program as the first argument, using the procedure I described above.

Since `execve` takes a string argument, you have to inject that string constant into the process's memory, either by overwriting some existing part of memory, or else allocating your own memory with `mmap`. I chose [the latter approach](https://github.com/iafisher/process-magic/blob/ae72fcaa8d7a3c5a149afd69a1f5eb28706ca729/src/proctool/pcontroller.rs#L491).

### Rewind a process
Rewinding a process is the same trick as taking it over, except that the process is taken over *by itself*. This is done by reading the program's original command line from `/proc/<pid>/cmdline` and then passing that as the argument to `execve`.

### Freeze a running process and thaw it later
This was the most complicated and open-ended trick. The real way to do it is with [CRIU](https://github.com/checkpoint-restore/criu), a mature project that handles many more cases. For my simple version, I just read the process's registers with `ptrace`, and its memory via ProcFS: `/proc/<pid>/maps` has the list of memory regions, and `/proc/<pid>/mem` has the actual memory.

The `thaw` command forks a child process and uses `ptrace` commands to set the registers, set up the memory maps via syscall injection of `mmap`, and [`process_vm_writev`](https://man7.org/linux/man-pages/man2/process_vm_readv.2.html) to write memory.

My implementation doesn't work with programs that allocate heap memory, I think because it doesn't save and restore the `brk` pointer properly. It also doesn't try to restore file descriptors.

### Manipulate program output
The ROT13 and colorizing standard error tricks used the same technique: intercept `write` syscalls using `PTRACE_SYSCALL` and tamper with the syscall arguments. For ROT13, this was easy because the transformation doesn't change the length of the string. Colorizing the output requires inserting [ANSI escape codes](https://en.wikipedia.org/wiki/ANSI_escape_code), which makes the string longer, so I had to call `mmap` to allocate new memory and copy the string over.

### Not done: Teleport a process to another terminal
Another trick I wanted to demonstrate was "teleporting" a process to an arbitrary terminal. I spent a lot of time on this, mainly following [this blog post](https://blog.nelhage.com/2011/02/changing-ctty/) about [`reptyr`](https://github.com/nelhage/reptyr), but ultimately couldn't get it working. `reptyr` "pulls" a process from its original terminal to the one that `reptyr` is running; what I wanted to do was teleport a process to an arbitrary terminal. I followed the arcane sequence of steps from the blog post to get a process to switch to another controlling terminal, and that worked, but the existing shell process in that terminal didn't cooperate with its new neighbor. In particular, they seemed to fight over input, with some input characters being read by the shell and some being read by the process.

One trick that is simple and doable is redirecting a process's output to another terminal. You can do this by closing the `stdout` file descriptor and reopening it to point to the desired `/dev/pts` device. But the process will still read input from its original terminal, and the new terminal will still be running the shell as its foreground process.

### Not done: Swap the memory of two processes
I wanted to demo swapping the memory of two running Python interpreters, so that symbols defined in one interpreter would be available in the other and vice versa. If I had done freezing and thawing correctly, this would have been a simple corollary: use the `freeze` procedure to grab the memory contents of one process, and use `thaw` to inject it into the other process.
