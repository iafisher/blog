#include <stdbool.h>
#include <stdlib.h>


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


typedef struct {
    size_t len, capacity;
    int* data;
} IntStack;


IntStack IntStack_new() {
    size_t capacity = 8;
    int* data = malloc(capacity * sizeof(int));
    if (!data) {
        /* TODO: Handle memory error. */
    }
    IntStack stck = { .len = 0, .capacity = capacity, .data = data };
    return stck;
}


void IntStack_free(IntStack* stck) {
    if (stck) {
        free(stck->data);
    }
}


size_t IntStack_length(IntStack* stck) {
    return stck ? stck->len : 0;
}


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


IntResult IntStack_pop(IntStack* stck) {
    if (!stck || stck->len == 0) {
        return IntResult_error();
    }

    stck->len--;
    return IntResult_of(stck->data[stck->len]);
}
