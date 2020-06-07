# Type-safe generic data structures in C
The rise of a new generation of low-level programming languages like Rust, Go and Zig has caused C and its primitive type system to fall into some disrepute. Nonetheless, with sufficient creativity it is possible to achieve surprisingly sophisticated results in C. One such result is generic data structures. This post reviews two techniques for implementing generic data structures in C: unsafely using raw memory and pointer casts, and safely using code generation through macros.[^background]


## Warm-up: an `int` stack
The generic data structure we will be implementing is a stack. As a warm-up, we'll write a regular, non-generic stack that only works for `int` values. Our minimalist stack will support only two operations, push and pop—not the most useful data structure, but enough to cover the fundamental challenges of data structure implementation.

Our stack's internal state consists of a length, a capacity, and a pointer to the stack's heap-allocated data. The length is the number of elements in the stack while the capacity is the maximum number of elements that the allocated memory could hold (not the size of the allocated memory in bytes, which is `capacity * sizeof(int)`).

```c
typedef struct {
    size_t len, capacity;
    int* data;
} IntStack;
```

*Aside:* You can find the full code for this post [here](https://github.com/iafisher/blog/tree/master/type_generic_c).

We'll start with the push operation. First, the stack is resized if there is not enough capacity for an additional element. Then, the stack's length is incremented and the value is written to the end of the data array:[^todo]

```c
void IntStack_push(IntStack* stck, int value) {
    if (!stck) {
        return;
    }

    if (stck->len + 1 > stck->capacity) {
        /* TODO: Handle arithmetic overflow. */
        size_t new_capacity = stck->capacity * 2;
        int* new_data = realloc(stck->data, new_capacity * sizeof(int));

        if (!new_data) {
            /* TODO: Handle memory error. */
            return;
        }

        stck->capacity = new_capacity;
        stck->data = new_data;
    }

    stck->len++;
    stck->data[stck->len - 1] = value;
}
```

Note that `realloc` may return a null pointer if it cannot re-allocate the memory, so it's not safe to assign the return value to `stck->data` without checking if it is null first. Also note that the use of `realloc` assumes that `stck->data` has been previously allocated with `malloc`, an assumption that will be upheld by the constructor that we'll write later.

The pop operation decrements the length field and returns the former last element. The return value is wrapped in an `IntResult` data structure, since in the case that `stck` is null or empty, there is no popped value to return.[^error]

```c
IntResult IntStack_pop(IntStack* stck) {
    if (!stck || stck->len == 0) {
        return IntResult_error();
    }

    stck->len--;
    return IntResult_of(stck->data[stck->len]);
}
```

`IntResult` and its constructors are defined as follows:

```c
typedef struct {
    bool error;
    int result;
} IntResult;

IntResult IntResult_of(int v) {
    IntResult r = { .error = false, .result = v };
    return r;
}

IntResult IntResult_error() {
    IntResult r = { .error = true };
    return r;
}
```

We'll also provide a constructor for the convenient creation of `IntStack` objects. It initializes the stack with a length of 0 and a small initial capacity of heap-allocated memory.

```c
IntStack IntStack_new() {
    size_t capacity = 8;
    int* data = malloc(capacity * sizeof(int));
    if (!data) {
        /* TODO: Handle memory error. */
    }
    IntStack stck = { .len = 0, .capacity = capacity, .data = data };
    return stck;
}
```

Since the constructor allocates memory from the heap, we need a corresponding destructor to free it:

```c
void IntStack_free(IntStack* stck) {
    if (stck) {
        free(stck->data);
    }
}
```

And with that, we have a minimal but complete stack class:

```c
IntStack int_stack = IntStack_new();
IntStack_push(&int_stack, 1);
IntStack_push(&int_stack, 2);
IntResult r = IntStack_pop(&int_stack);
assert(!r.error);
assert(r.result == 2);
IntStack_free(&int_stack);
```


## Unsafe generic stack
`IntStack` only works for `int` values. If you wanted a `char` stack, you would have to write a another stack implementation. And if you did so, you would find that the code for `CharStack` is nearly identical to the code for `IntStack`, because the stack, like most container data structures, doesn't manipulate its elements in any way, it just stores them. The only thing it needs to know about them is how much memory each one of them occupies. So rather than writing different stacks for every element type, let's try writing a stack that works for any element type.

The critical insight is that, even though at compile time neither the type nor the size of the elements is known, the elements of the stack can still be stored as unstructured binary data as long as we keep track of how much memory each element occupies.

In C, binary data can be stored by in an array of `char`s. To give an example, suppose we define a `Point` type:

```c
typedef struct {
    int x, y;
} Point;
```

We can store a `Point` object in a `char` array like this, using `memcpy` to copy the bytes into the array:

```c
// Initialize an array with more than enough capacity.
char data[100];

// Initialize a Point object.
Point p = { .x = 42, .y = 43 };

// Copy the Point object into the array.
memcpy(data, &p, sizeof(Point));

// Print the bytes of the array.
for (size_t i = 0; i < sizeof(Point); i++) {
    printf("data[%ld] = %d\n", i, data[i]);
}
```

On my system, the for loop prints

```
data[0] = 42
data[1] = 0
data[2] = 0
data[3] = 0
data[4] = 43
data[5] = 0
data[6] = 0
data[7] = 0
```

But the individual elements of the array must be treated as opaque because the memory layout of `Point` is up to the compiler.

This technique is the foundation of our generic stack type, `UnsafeStack`.[^glib] `UnsafeStack` has a `char* data` field instead of `int* data`, and an additional `objsize` field to track how many bytes each object occupies:

```c
typedef struct {
    size_t len, capacity;
    size_t objsize;
    char* data;
} UnsafeStack;
```

The logic of resizing the array in `UnsafeStack_push` is similar to that of `IntStack_push`. As we saw in the `Point` example, we have to use `memcpy` to copy the value to the end of the stack, rather than assigning it directly to an index of the array, because the value could be arbitrarily large. `UnsafeStack_push` accepts a value of type `void*` so that any objects of any type can be passed to it.

```c
void UnsafeStack_push(UnsafeStack* stck, void* value) {
    if (!stck) {
        return;
    }

    if (stck->len + 1 > stck->capacity) {
        size_t new_capacity = stck->capacity * 2;
        char* new_data = realloc(stck->data, new_capacity * stck->objsize);

        if (!new_data) {
            /* TODO: Handle memory error. */
            return;
        }

        stck->capacity = new_capacity;
        stck->data = new_data;
    }

    memcpy(stck->data + (stck->len * stck->objsize), value, stck->objsize);
    stck->len++;
}
```

Similarly, `UnsafeStack_pop` returns a pointer of type `void*`, because the type of the objects in the data structure isn't known at compile time. The pointer is an offset into the array calculated as `stck->len * stck->objsize`:

```c
void* UnsafeStack_pop(UnsafeStack* stck) {
    if (!stck || stck->len == 0) {
        return NULL;
    }

    stck->len--;
    return stck->data + (stck->len * stck->objsize);
}
```

Errors can be signalled by returning a null pointer, so we don't need a `Result` object for `UnsafeStack`.

`UnsafeStack_new` and `UnsafeStack_free` are very similar to before:

```c
UnsafeStack UnsafeStack_new(size_t objsize) {
    size_t capacity = 8;
    char* data = malloc(capacity * objsize);
    if (!data) {}
    UnsafeStack stck = { .len = 0, .capacity = capacity, .objsize = objsize, .data = data };
    return stck;
}

void UnsafeStack_free(UnsafeStack* stck) {
    if (stck) {
        free(stck->data);
    }
}
```

`UnsafeStack`'s API is a bit different from `IntStack`'s. When pushing a value onto the stack, we provide a pointer to it rather than the element itself, and when popping a value, we cast the return value and then de-reference it.

```c
UnsafeStack_push(&unsafe_stack, &i);
int v = *(int*)UnsafeStack_pop(&unsafe_stack);
```

Since `UnsafeStack_push` accepts a pointer argument, we cannot pass integer literals to it.


## Safe generic stack using macros
Unlike casts in Java and [type assertions](https://golang.org/ref/spec#Type_assertions) in Go, casts in C are entirely unsafe. The compiler will not complain at compile time and the program will not throw an exception at runtime if the cast is invalid. Rather, it will silently continue on to do strange and terrible things, like accessing uninitialized memory or overwriting memory belonging to other variables. Since C is a statically typed language, we would prefer to avoid these possible errors.

Let's return to the fundamental problem. If we want type-safe stacks, then we have to write a different, though virtually identical, implementation for each type. It's essentially a problem of code duplication.

Fortunately, C has a mechanism for dealing with code duplication: macros. Rather than writing out a full stack implementation for each type, we can use a macro to generate it for us from a template. We will take our `IntStack` implementation, replace all uses of `int` with a `type` parameter, and then wrap the whole implementation in a macro that is parameterized on `type`. Whenever we want to use a stack for a new type, we'll call the macro to generate the code for the implementation. As far as the C compiler is concerned, it's as if we wrote a separate implementation for each type *with the concrete types in the code* so that the compiler can type-check the code properly.

The macro code is a little hard to read, not the least because each line must end with a backslash to continue the macro on to the next line, but it is recognizably almost the same code as for `IntStack`. The syntax `typename##_new`, `typename##_free`, etc., tells the preprocessor to glue `typename`, a macro parameter, to literal strings like `_new` or `_free`, yielding results like `FloatStack_new` or `StringStack_free`. The macro parameter `type` is substituted wherever we had `int` in the original `IntStack` code.

```c
#define DECL_STACK(typename, type) \
    typedef struct { \
        size_t len, capacity; \
        type* data; \
    } typename; \
    \
    typedef struct { \
        bool error; \
        type result; \
    } typename##Result; \
 \
    typename typename##_new() { \
        size_t capacity = 8; \
        type* data = malloc(capacity * sizeof(type)); \
        if (!data) {} \
        typename stck = { .len = 0, .capacity = capacity, .data = data }; \
        return stck; \
    } \
 \
    void typename##_free(typename* stck) { \
        if (stck) { \
            free(stck->data); \
        } \
    } \
 \
    size_t typename##_length(typename* stck) { \
        return stck ? stck->len : 0; \
    } \
 \
    void typename##_push(typename* stck, type value) { \
        if (!stck) { \
            return; \
        } \
 \
        if (stck->len + 1 > stck->capacity) { \
            size_t new_capacity = stck->capacity * 2; \
            type* new_data = realloc(stck->data, new_capacity * sizeof(type)); \
 \
            if (!new_data) { \
                return; \
            } \
 \
            stck->capacity = new_capacity; \
            stck->data = new_data; \
        } \
 \
        stck->len++; \
        stck->data[stck->len - 1] = value; \
    } \
 \
    typename##Result typename##_pop(typename* stck) { \
        if (!stck || stck->len == 0) { \
            typename##Result errorval = { .error = true }; \
            return errorval; \
        } \
 \
        type value = stck->data[stck->len - 1]; \
        stck->len--; \
        typename##Result r = { .error = false, .result = value }; \
        return r; \
    }
```

We then call `DECL_STACK` to declare a new stack type, either in a header file or at the top level of a program:

```c
DECL_STACK(SafeIntStack, int)
```

The resultant API achieves the safety and convenience of `IntStack` and the generality of `UnsafeStack`:

```c
SafeIntStack safe_int_stack = SafeIntStack_new();
SafeIntStack_push(&safe_int_stack, 1);
SafeIntStack_push(&safe_int_stack, 2);
SafeIntStackResult r = SafeIntStack_pop(&safe_int_stack);
assert(!r.error);
assert(r.result == 2);
SafeIntStack_free(&safe_int_stack);
```

Note that `SafeIntStack` is still only as safe as C's type system, which will, for example, allow you to use a string literal where an `int` is expected, with only a compiler warning. This is a fundamental limitation that cannot be worked-around.

The safe stack data structure has no overhead above hand-written code, except that each new declaration increases the program size by a constant amount (unlike the unsafe stack, which uses the same code for all data structures). Incidentally, this code generation technique is essentially how templates are implemented behind the scenes in C++.

That it is possible to write type-safe generic data structures in a language whose type system does not natively support them speaks to C's flexibility.[^cello] But the techniques we used—unchecked pointer casts and unsanitary lexical macros—are themselves quite unsafe if used improperly. Flexibility, simplicity and safety: a language can attain at most two out of three. Rust and Haskell choose flexibility and safety. Go chooses safety and simplicity.[^go] C chooses flexibility and simplicity. Each choice has its trade-offs. The tendency for modern languages to prefer safety is a direct consequence of the innumerable bugs found in C code that could have been prevented by stronger compile-time guarantees. Nonetheless, as this post has shown, flexibility and simplicity are a powerful combination.


[^background]: I assume the reader is proficient in C. The classic text on C is *The C Programming Language* by Brian Kernighan and Dennis Ritchie, universally known as *K&R* after the author's initials. Look for the second edition. Though *K&R* has aged remarkably well, best practices have been refined and some language features have changed since 1988. [*Modern C*](https://modernc.gforge.inria.fr/) by Jens Gustedt is a great re-introduction to the modern language.

[^todo]: Here and throughout I've added `TODO`s to mark where a more robust implementation would need to handle an edge case.

[^error]: Traditionally, error handling in C is done either by returning a special error value, or "out-of-band" by setting the global `errno` variable. I find the latter approach inelegant, and the former is impossible because any `int` value is a possible legal return value of `IntStack_pop`.

[^glib]: [GLib](https://wiki.gnome.org/Projects/GLib), the utility library for the GNOME desktop environment, uses this technique for its [`garray`](https://gitlab.gnome.org/GNOME/glib/-/blob/master/glib/garray.h) generic array type.

[^cello]: For more evidence, see Daniel Holden's [Cello](https://github.com/orangeduck/Cello), a framework for high-level programming in C.

[^go]: Debatable, perhaps. Go does allow some unsafe constructs like `interface{}`, but it largely abandons the reckless permissiveness of C.
