# Writing an interpreter and debugger for an assembly language
The computer science department at my college taught assembly programming using a custom architecture called the [Haverford Educational RISC Architecture](https://www.haverford.edu/computer-science/resources/hera) language and universally known as HERA.[^pronounce] The department provided a shell script called `HERA-C-Run` to run HERA programs. Unfortunately, `HERA-C-Run` suffered from several shortcomings. It was slow, buggy, didn't implement the full language specification, produced exceptionally verbose and unhelpful error messages, and lacked a purpose-built debugger.[^gplusplus] In the fall of my senior year of college, I became sufficiently frustrated with `HERA-C-Run` that I wrote my own program in Python to replace it, which I dubbed `hera-py`.

This post describes how I used **declarative programming** to concisely define HERA operations in `hera-py`, and how I wrote an **interactive debugger** for troubleshooting HERA programs.

You can read the source code of `hera-py` on [GitHub](https://github.com/iafisher/hera-py), and you can sample the HERA language using [the online sandbox](https://iafisher.com/projects/hera).


## The HERA assembly language
First, a brief overview of the HERA language. We will learn the fundamentals by translating some simple Python programs into HERA.[^asm]

First, let's try assigning some values to local variables and adding them together:

```python
a = 20
b = 22
c = a + b
```

To store values locally, HERA uses a fixed set of 16 *registers* that are identified by the symbols `R1`, `R2`, etc. up to `R16`.[^registers] Let's (arbitrarily) pick `R2` for `a`, `R3` for `b`, and `R1` for `c`.

The HERA operation `SET` places a value into a register, and `ADD` adds the contents of two registers together. Thus, our first HERA program is:[^forty-two]

```cpp
SET(R2, 20)
SET(R3, 22)
ADD(R1, R2, R3)
```

`ADD` is a ternary operation. Like most ternary operations in HERA, the first register listed is the destination, so `ADD(R1, R2, R3)` means `R1 = R2 + R3`. HERA has `SUB` and `MUL` operations as well, although not `DIV`.[^division]

Let's try something a bit more complex:

```python
if x < y:
    print(y)
else:
    print(x)
```

Like most assembly languages, HERA lacks control-flow structures like `if` statements and loops. Instead, the flow of execution is controlled using *branches* and *labels*. Here's an example:

```cpp
BR(skip)
SET(R1, 666)
LABEL(skip)
SET(R2, 42)
```

`BR` is an unconditional branching operation, meaning that it always causes the machine to jump to the given label, like a `goto`. In this case, it jumps over the instruction `SET(R1, 666)` and proceeds directly to `SET(R2, 42)`.

Besides `BR`, HERA includes a set of conditional branching operations: if the branch's condition (less-than, greater-than, etc.) is met, then the machine jumps to the label; otherwise, it moves on to the next instruction. Conditional branches are typically used immediately after a `CMP` instruction, which compares the contents of two registers.[^cmp] The program below uses the `BLE` instruction to skip `SET(R1, 666)` if `R1` is less than or equal to `R2`.

```cpp
CMP(R1, R2)
BLE(skip)
SET(R1, 666)
LABEL(skip)
```

Using both conditional and unconditional branches, we can implement our Python `if` statement in HERA:

```cpp
CMP(R2, R3)
BL(true_clause)
BR(false_clause)

LABEL(true_clause)
print_reg(R3)
BR(end)

LABEL(false_clause)
print_reg(R2)

LABEL(end)
```

First, the `CMP`-`BL` sequence checks if `R2` is less than `R3`. If it is, then the machine jumps to the "true" clause. If it isn't, then the machine continues on to the next instruction, `BR`, which unconditionally jumps to the "false" clause. The two branching operation create two disjoint paths for the flow of control.

In the "true" clause (the two instructions after `LABEL(true)`), we print the contents of `R3` with `print_reg` (a helpful debugging aid although not a real HERA instruction). After we print the register, we jump to the end of the "false" clause so that we don't execute it. The "false" clause is similar except that it has no jump at the end, since the end of the "false" clause is also the end of the `if` statement as a whole so we don't need to jump as we are already there.

If you find the explicitness of this example perplexing, remember that we are defining the semantics of an `if` statement ourselves. The machine doesn't know anything about "true" and "false" clauses and will happily execute one after the other unless we tell it not to.

Once you get the hang of it, translating high-level control-flow constructs into assembly turns out to be quite formulaic. A `while` loop like

```python
while x > y:
    # body of the loop
```

becomes

```cpp
LABEL(start)
CMP(R2, R3)
BLE(end)
// body of the loop
BR(start)
LABEL(end)
```

A comparison at the beginning jumps past the loop if it is false, and an unconditional branch at the end of the loop jumps back to the beginning for the next iteration.

The information presented so far can be generalized into a simple but complete mental model of how HERA programs execute. The processor holds a special value called the *program counter*, which stores the index of the current instruction, starting at 0.[^program-counter] After a normal operation (i.e., not a branch), the processor increments the program counter. After a branch, the processor may either increment it (if the branch was false) or assign the value of the branch's label to it (if the branch was true), so that the next instruction the processor executes is after the branch's label. Once the program counter is incremented past the last instruction, the machine halts. We will encounter see this mental model translated into Python when we look at the design of the `hera-py` interpeter in the next section.

Not all of the operations that we have seen are "real" HERA operations that the architecture provides; a few of them are assembly-language constructs that are converted to other operations before they are executed. `SET` is an example. The HERA architecture has no `SET` operation, only `SETLO` and `SETHI` to set the low and high 8 bits of a register, respectively. The reason for this is that HERA is a 16-bit architecture, meaning that registers, memory addresses, memory locations, and machine code instructions are all 16 bits wide. Since a machine instruction is encoded in 16 bits, it wouldn't be possible for `SET` to be a single machine operation, because it would need 16 bits for the value plus 4 bits to identify the register. For convenience, the HERA assembly language provides a 16-bit `SET` operation which translates to a `SETLO`-`SETHI` sequence.

Labels, and branches that take labels directly, are also assembly-language features. In the HERA architecture, branches specify the exact index of the instruction to branch to. Without labels, HERA programmers would have to hard-code line numbers into each branching operation, and remember to update them whenever the lines of the program changed. This is tedious and highly error-prone, so the HERA language lets you identify locations in the source code with labels, and calculates the location itself when translating the assembly code into machine code.

This has been a whirlwind tour of the HERA language that covered the fundamentals with a few notable omissions which I will briefly note here:

- In addition to the registers, HERA programs can also store values in main memory using the `LOAD` and `STORE` instructions.

- HERA has a primitive mechanism for calling functions using the `CALL` and `RET` operations, which handle control flow, though the programmer is responsible for putting the arguments in the right place, retrieving the return value, managing the call stack and avoiding trampling on other functions' values.

- Branches in the HERA architecture come in two flavors: absolute branches that accept a register argument and set the program counter to the value of the register, and relative branches that specify a relative offset. Both flavors accept labels in the HERA assembly language, so the distinction is largely irrelevant to HERA programmers.[^rel-abs-branch]

- HERA has commands for initializing the static data segment of the program with values such as string literals.

A full PDF reference for the HERA language at one point existed on [Haverford's website](https://www.haverford.edu/computer-science/resources/hera) but has evidently gone missing. If you would like a copy, you can email me at iafisher@protonmail.com.


## Reducing code duplication with declarative programming
The heart of `hera-py` is the interpreter, the component that runs HERA programs. In addition to the interpreter, `hera-py` includes an assembler, disassembler[^disassembler] and debugger. Each tool shares the same front-end for lexing and parsing HERA programs, and for converting assembly-language features into pure HERA.

When I first implemented the interpreter, its core was in essence a software simulation of an actual HERA processor:

```python
class VirtualMachine:
    def __init__(self):
        # NOTE: In Python, `[0] * 16` is short-hand for a list of 16 zeros.
        self.registers = [0] * 16
        self.flags = (False, False, False, False, False)
        self.memory = [0] * (2**16)
        self.pc = 0

    def execute(self, program):
        while self.pc < len(program):
            self.execute_instruction(program[self.pc])

    def execute_instruction(self, i):
        if i.name == "ADD":
            self.registers[i.args[0]] = self.registers[i.args[1]] + self.registers[i.args[2]]
            self.pc += 1
        elif i.name == "SUB":
            ...
```

The `execute` method encapsulates the logic of executing an entire program, matching the mental model described earlier, and `execute_instruction` defines the semantics of each HERA operation.

This design is simple and logical, but it risked splitting the definition of each HERA operation between four different places: the interpreter's virtual machine, for the operation's behavior; the typechecker, for its type signature; and the assembler and the disassembler, for its binary representation.

To avoid duplication, I extracted the operations from the individual tools and consolidated them [in one place in their own module](https://github.com/iafisher/hera-py/blob/v1.0.2/hera/op.py), where each operation is defined by a Python class: what kinds of operands it takes (registers, labels, integers, etc.), how it executes (for the interpreter), and how it translates to machine code (for the assembler and disassembler).

Here's an example:

```python
# https://github.com/iafisher/hera-py/blob/v1.0.2/hera/op.py#L729

class SAVEF(AbstractOperation):
    """
    SAVEF(Rd)
      Save the flags to Rd. The flags are stored in the following bits:
        0: sign
        1: zero
        2: overflow
        3: carry
        4: carry-block
      The higher bits of Rd are set to 0.
    """

    P = (REGISTER,)
    BITV = "0011 AAAA 0111 0000"

    def execute(self, vm):
        value = (
            int(vm.flag_sign)
            + 2 * int(vm.flag_zero)
            + 4 * int(vm.flag_overflow)
            + 8 * int(vm.flag_carry)
            + 16 * int(vm.flag_carry_block)
        )
        vm.store_register(self.args[0], value)
        vm.pc += 1
```

`P` and `BITV` define the operation's type signature and binary representation, respectively, using a *declarative programming* style, meaning that they merely declare the type signature and representation without specifying how to typecheck a concrete operation or convert it into its binary representation. The imperative logic for doing so resides elsewhere, on the `AbstractOperation` super-class, so that the definitions of each operation are kept concise and readable.

The declarative approach comes with a trade-off compared to writing concrete `typecheck`, `assemble` and `disassemble` methods on each operation, which is that the generic versions of these methods on `AbstractOperation` are necessarily more complex than any of the concrete methods would have been. In this case, avoiding massive code duplication across dozens of HERA operations outweighed the extra complexity, but in cases where the number of uses is fairly small, a declarative approach may not be suitable.

The brevity of the code was aided by the object-oriented style, as similar operations could inherit from a common super-class to reuse common behavior. This was especially effective for branches:

```python
# https://github.com/iafisher/hera-py/blob/v1.0.2/hera/op.py#L936

class BL(RegisterBranch):
    """
    BL(label)
      Jump to the given label if either the sign flag or the overflow flag are on, but
      not if both are.
      Run `doc branch` for a detailed explanation of branching instructions.
    """

    BITV = "0001 0010 0000 AAAA"

    @staticmethod
    def should(vm):
        return vm.flag_sign ^ vm.flag_overflow
```

The `P` field can be omitted entirely since all branches have the same type signature, and the `execute` method is simplified to a `should` method that decides whether to branch or not based on the state of the virtual machine. Thus execution, typechecking, assembly and disassembly are all implemented for `BL` with only two unique lines of code.


## Writing a debugger for HERA
The `hera-py` debugger lets you step through the execution of the program, examine and change the virtual machine's state, set breakpoints, view documentation for each HERA operation,[^docstring] view the implicit call stack, and undo debugging operations an unlimited number of times. It supports an arithmetic mini-language for doing quick computations in the debugger shell, and the results of these computations can be assigned back to registers and memory locations in HERA. It can assemble, disassemble and execute user-provided HERA operations on the fly.

There are at least two ways to write a debugger. The first way is to use debugging operations provided by the execution environment (e.g., the operating system for compiled programs or the interpreter for interpreted ones) to probe and control the program as it runs. The advantage of this approach is that the program runs in the same environment as under regular execution, so its behavior should be the same. [gdb](https://blog.0x972.info/?d=2014/11/13/10/40/50-how-does-a-debugger-work) and [pdb](https://github.com/python/cpython/blob/v3.6.9/Lib/bdb.py#L432) are both implemented this way.

The second way is for the debugger to run the program itself, like a special-purpose language interpreter. The debugger has full control over the execution of the program, but must be careful not to change its semantics, lest the program behave differently under debugging. [Valgrind](https://valgrind.org/docs/manual/manual-core.html#manual-core.whatdoes) and the `hera-py` debugger are implemented this way.

Since the interpreter already runs HERA programs by executing the instructions step-by-step, just as the debugger does, the core logic of the debugger was [straightforward to write](https://github.com/iafisher/hera-py/blob/v1.0.2/hera/debugger/debugger.py#L105). Under normal execution, the interpreter executes the instructions in a loop, always choosing the next instruction according to the program counter. Rather than using a loop, the debugger executes instructions according to user commands like `next` and `step`. Naturally, the debugger has no particular knowledge of individual HERA operations. It just calls the operation's `execute` method, as the interpreter does.

It took some cleverness to make it appear to the user that the original operations of the program are being executed even though some of them (the assembly-language features mentioned earlier) had been compiled down to simpler operations. The preprocessor handles this illusion by attaching a reference to the original operation when it translates it away. The debugger knows to always execute instructions that came from the same original operation as a unit, so that, for example, when the user enters `next` on a `SET` instruction, the debugger executes both the underlying `SETLO` and `SETHI` instructions.

The debugger uses a modular design in which a [`Debugger`](https://github.com/iafisher/hera-py/blob/v1.0.2/hera/debugger/debugger.py) class implements the core logic of debugging while a separate [`Shell`](https://github.com/iafisher/hera-py/blob/v1.0.2/hera/debugger/shell.py) class handles user interaction. This is analogous to the difference between the [bdb](https://docs.python.org/3.6/library/bdb.html) and [pdb](https://docs.python.org/3.6/library/pdb.html) modules in the Python standard library.

To allow unlimited undoing, the debugger makes a full copy of its state and the virtual machine after each mutating operation, and retains a reference to the previous version. The previous version in turn keeps a reference to the version prior to it, forming an implicit linked list of the debugger and virtual machine's entire history. Methods on the debugger class are thus free to change the debugger's internal state however they wish, as long as they are annotated with `@mutates` which tells the debugger to save a copy of itself before executing the method. Of course, this technique is not very memory-efficient, though the cost is mitigated by [special logic](https://github.com/iafisher/hera-py/blob/v1.0.2/hera/vm.py#L43-L46) in the virtual machine that allocates memory on-demand.

The syntax for the debugger's mini-language is actually more complex than the syntax of HERA itself, because it supports nested expressions and infix arithmetic operators. The debugger has [its own parser](https://github.com/iafisher/hera-py/blob/v1.0.2/hera/debugger/miniparser.py) that uses the Pratt parsing technique for handling infix operator precedence, a technique I learned from Thorsten Ball's [*Writing an Interpreter in Go*](https://interpreterbook.com/).


## Conclusion
`hera-py` was an interesting challenge. For the most part, standard techniques for programming language implementation proved suitable for an assembly-language interpreter as well. By using object-oriented and declarative programming techniques, the definition of individual HERA operations was accomplished quite concisely. The implementation of the debugger was aided by the inherently step-by-step nature of assembly programs as well as the simplicity of HERA's execution model.


[^pronounce]: Pronounced /hɛrə/ (HAIR-uh).

[^gplusplus]: `HERA-C-Run` took your HERA program, wrapped it in some C++ boilerplate, and pasted a few `#include` directives at the top to include libraries that defined the HERA operations as C++ preprocessor macros. Then, it called `g++` to compile the ad-hoc C++ program that it just created, and it executed the binary that `g++` produced. If you thought that `g++` gave bad error messages for regular C++, you would not want to contemplate how bad the error messages were for what was essentially a domain-specific language implemented with the C++ preprocessor. And you can hardly begin to imagine how painful it was to debug your HERA programs with `gdb`, especially for the poor souls straight out of Introduction to Data Structures who had never even heard of C++.

[^asm]: This section assumes familiarity with the fundamentals of assembly programming. My favorite introduction to assembly languages is the book [*Programming from the Ground Up*](https://savannah.nongnu.org/projects/pgubook/) by Jonathan Bartlett. Note that *Programming from the Ground Up* uses 32-bit x86, while your computer likely uses 64-bit, so most of the example programs will not run without (slight) modification.

[^registers]: HERA programmers usually use only `R1` through `R10` as `R11` through `R16` are reserved by convention for special purposes.

[^forty-two]: Those who took Dave Wonnacott's compilers course at Haverford will recognize that most of the programs in the grading rubric concluded by setting `R1` to 42. We joked that you could get halfway through the semester with a compiler that ignored the input program and always emitted `SET(R1, 42)`.

[^division]: HERA has no `DIV` because it would be too difficult to implement a division circuit in hardware in the computer architecture class, and because (integer) division can be implemented in software using `ADD` and `SUB`. In compilers, we were provided with a HERA "standard library" that included a `div` subroutine, which is how we compiled programs that used division. Incidentally, while much of the standard library was written in pure HERA that `hera-py` could run, significant portions of it were written in C++. As I couldn't stomach re-writing the C++ parts in HERA, I added [a secret operation](https://github.com/iafisher/hera-py/blob/v1.0.2/hera/op.py#L1838) to embed Python code inside of a HERA program, so that I could just translate the C++ to Python. The C++ bits of the standard library are also why half the logic in [the parser](https://github.com/iafisher/hera-py/blob/v1.0.2/hera/parser.py) is devoted to achieving a minimal level of compatibility with C++ preprocessor directives.

[^cmp]: `CMP` "communicates" with the subsequent branching operation through *flags*, a set of five bits in the machine that HERA operations can flip. Conditional branches decide whether to branch or not based on the values of one or more flags. You could have set the flags manually instead of using `CMP` and achieved the same result.

[^program-counter]: Note that the program counter doesn't correspond exactly to the lines of the program, due to blank lines, comments, operations that don't produce any machine code, and assembly-language operations that produce multiple machine instructions.

[^rel-abs-branch]: Register branches can be used to implement higher-order functions in languages that compile to HERA. Prior to `hera-py` this was not possible. Unfortunately I started working on `hera-py` after I completed the compilers course so I never got the chance to try this technique myself.

[^disassembler]: Besides disassembling HERA binaries, the disassembler is used to implement the special HERA operation `OPCODE`, which lets you write binary code directly in HERA, e.g. `OPCODE(0b1010000100100011)`. If you want to annoy your TAs and professors you can run `hera preprocess --obfuscate` over your program before submitting it for grading to convert every operation to an opaque `OPCODE`.

[^docstring]: A little trick that I'm especially fond of is that the debugger uses the docstring of the HERA operation's class as its that operation's help message.
