# A subtle garbage collector bug
According to GitHub, I've found 159 bugs in my own code.[^bugs] Of these 159, one bug sticks out as my most memorable.

I was in the midst of implementing a mark-and-sweep garbage collector for [Scam](https://github.com/iafisher/scam), a Lisp dialect based on Daniel Holden's [*Build Your Own Lisp*](http://www.buildyourownlisp.com/). A mark-and-sweep garbage collector works by

1. Iterating over a "root set" of objects known to be reachable (e.g., all objects in the call stack).

2. Recursively traversing the graph of objects reachable from the root set from step 1, and marking each of these objects as reachable.

3. Freeing all allocated objects that were not marked reachable in step 2.

Mark-and-sweep is far from the most efficient garbage collection technique—the program has to halt entirely while collection is running, and the program's entire working memory has to be examined—but it is simple to implement. The collector keeps an array of all objects that are currently allocated. Each object has a bit for whether it is a root object and a bit for whether it is currently reachable. Objects are automatically marked as root objects when allocated, and unmarked when they go out of scope.[^out-of-scope] Garbage is collected whenever allocation fails (i.e., whenever `malloc` or `realloc` returns `NULL`).

While testing the garbage collector with [Valgrind](https://valgrind.org/), I discovered that under certain murky circumstances, the array copying subroutine would fail due to a segmentation fault.

Here is the code of the subroutine at the time of the bug. Can you spot it?[^annotated]

```c
scamval* gc_copy_scamval(scamval* v) {
    // Switch on the type (in Scam, not in C) of the object we are copying.
    switch (v->type) {
        // In case the object is a list or an S-expression:
        case SCAM_LIST:
        case SCAM_SEXPR:
        {
            // Allocate a new scamval.
            scamval* ret = scamval_new(v->type);
            // Allocate enough memory for the array.
            // In this version of Scam, values were represented as tagged
            // unions, where `val` is the union field and `vals.arr` is the
            // array variant of the union.
            ret->vals.arr = my_malloc(v->count * sizeof *v->vals.arr);
            // Set the length and capacity of the array.
            ret->count = v->count;
            ret->mem_size = v->count;
            // Recursively copy over each element of the old array.
            for (int i = 0; i < v->count; i++) {
                ret->vals.arr[i] = gc_copy_scamval(v->vals.arr[i]);
            }
            return ret;
        }
        // code for copying other types of Scam values...
    }
}
```

The problem is that the length of the new array is set before the new elements are copied over. Thus, while it is being copied the array claims to be `n` elements long, but not all of those elements actually exist. When the garbage collector is invoked while the array is in this partially initialized state, the mark subroutine iterates over the array and tries to access the nonexistent elements, and mayhem ensues.

Finding and triaging this bug was unusually difficult. In my naive implementation garbage collection only occurred when the program literally ran out of memory, so in order to test the collector I had to artificially restrict the size of the heap. Merely invoking the garbage collector manually wouldn't have caught this bug, which only occurred when the garbage collector ran in the middle of the array copying subroutine. Although Valgrind told me that the invalid memory access occurred in the `gc_copy_scamval` function, I couldn't assume that the bug was in that function, because often garbage collection bugs are caused by memory errors in other parts of the interpreter that don't surface until the garbage collector runs. To find the bug I eventually resorted to simulating the execution of the program with paper and pencil.

The simple fix was to increment the size of the array after each element is copied into it. The enduring lesson was that all data structures must be in a consistent state before a subroutine tries to allocate memory.[^or-rust]


[^bugs]: Don't tell my boss.

[^out-of-scope]: That is, when they go out of scope in the Lisp program that the interpreter, written in C, is running, not in the C program itself.

[^annotated]: I've annotated [the original source code](https://github.com/iafisher/scam/blob/3b5a8613ca767f34b2659a15223bc988dcfc29ad/collector.c#L133-L143) with explanatory comments.

[^or-rust]: Or use [a language](https://www.rust-lang.org/) that precludes the occurrence of this type of error.
