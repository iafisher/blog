# Append-only programming
I have recently adopted a new methodology of software development:

1. Everything goes in a single C file.
2. New code is appended to the end of the file.
3. Existing code cannot be edited.

I call it *append-only programming*.

Append-only programming has many benefits. It forces you to define your interfaces before your implementations. It encourages you to write small functions. And it produces source code that is eminently readable, because the text of the program recapitulates your train of thought – a kind of stream-of-consciousness [literate programming](https://en.wikipedia.org/wiki/Literate_programming).

Make no mistake: append-only programming is not the most forgiving paradigm. If a subprocedure is found to be erroneous, a corrected version must be appended, and all of its callers must likewise be corrected. In unfortunate cases, the entire program may need to be retyped. The programmer is thus advised to get it right the first time.

Rather than use a conventional text editor, I prefer to simply `cat >> main.c`, which ensures that rules (2) and (3) are strictly observed. In fact, with a couple of aliases, I [never need to leave the shell](https://blog.sanctum.geek.nz/series/unix-as-ide/) at all:

```
alias edit='cat >> main.c'
alias show='less main.c'
alias check='gcc -Wall -c main.c'
alias build='gcc -Wall main.c'
alias checkpoint='git add main.c && git commit -m "."'
alias revert='git restore main.c'
```

---

In all seriousness, append-only programming is just a fun challenge, not a legitimate way of writing software. I wrote a [small Lisp interpreter](https://github.com/iafisher/append-only) in append-only fashion, and it got tedious around the third time I had to re-type `eval_string`.

My original idea was that, since C lets you forward-declare types and functions, you could write a program incrementally: start by defining the `main` function in terms of high-level helper functions, then write those helper functions in terms of slightly lower-level functions, and so on until the entire program is complete. It's a sensible approach, and one that I often use in practice.

Of course, real coding rarely proceeds so smoothly, and you often discover, in the middle of writing your low-level functions, that your high-level functions need to be revised, which append-only programming makes difficult. Even more difficult is troubleshooting code that is not working. It is not an especially compelling use of my time to re-type an entire function just to add `print` statements.

Append-only programming was a noble experiment, but perhaps not one that it would be fruitful to repeat. If this post does inspire you to try it yourself, I'd recommend a couple of revisions that preserve the spirit while easing some of the monotonous parts:

- Split out a `main.h` header file, so that you can append declarations and imports independently of definitions.
- Split your program into one file for every function, and allow yourself to overwrite files.

For those of you feeling even more adventurous, may I suggest append-only blogging? Or is that just Twitter?
