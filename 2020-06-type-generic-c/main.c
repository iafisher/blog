/**
 * Compile with gcc -o main -Wall -g main.c
 */
#include <assert.h>
#include <stdio.h>
#include "int_stack.h"
#include "unsafe_stack.h"
#include "safe_stack.h"


typedef struct {
    int x, y;
} Point;


DECL_STACK(SafeIntStack, int)
DECL_STACK(PointStack, Point)


int main() {
    IntStack int_stack = IntStack_new();
    for (int i = 5000; i < 6000; i++) {
        IntStack_push(&int_stack, i);
    }
    assert(IntStack_length(&int_stack) == 1000);
    for (int i = 5999; i >= 5000; i--) {
        IntResult r = IntStack_pop(&int_stack);
        assert(!r.error);
        assert(r.result == i);
    }
    IntStack_free(&int_stack);


    UnsafeStack unsafe_stack = UnsafeStack_new(sizeof(int));
    for (int i = 5000; i < 6000; i++) {
        UnsafeStack_push(&unsafe_stack, &i);
    }
    assert(UnsafeStack_length(&unsafe_stack) == 1000);
    for (int i = 5999; i >= 5000; i--) {
        int* vp = UnsafeStack_pop(&unsafe_stack);
        assert(vp);
        assert(*vp == i);
    }
    UnsafeStack_free(&unsafe_stack);


    SafeIntStack safe_int_stack = SafeIntStack_new();
    for (int i = 5000; i < 6000; i++) {
        SafeIntStack_push(&safe_int_stack, i);
    }
    assert(SafeIntStack_length(&safe_int_stack) == 1000);
    for (int i = 5999; i >= 5000; i--) {
        SafeIntStackResult r = SafeIntStack_pop(&safe_int_stack);
        assert(!r.error);
        assert(r.result == i);
    }
    SafeIntStack_free(&safe_int_stack);


    PointStack point_stack = PointStack_new();
    for (int i = 5000; i < 6000; i++) {
        Point p = { .x = i, .y = -i };
        PointStack_push(&point_stack, p);
    }
    assert(PointStack_length(&point_stack) == 1000);
    for (int i = 5999; i >= 5000; i--) {
        PointStackResult r = PointStack_pop(&point_stack);
        assert(!r.error);
        assert(r.result.x == i);
        assert(r.result.y == -i);
    }
    PointStack_free(&point_stack);

    /* Compiler error:
     *
     *   PointStack another_safe_stack = PointStack_new();
     *   PointStack_push(&another_safe_stack, "Hello, world!");
     *
     */

    puts("Tests passed!");
    return 0;
}
