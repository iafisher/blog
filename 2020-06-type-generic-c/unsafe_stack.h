#include <stdlib.h>
#include <string.h>


typedef struct {
    size_t len, capacity;
    size_t objsize;
    char* data;
} UnsafeStack;


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


size_t UnsafeStack_length(UnsafeStack* stck) {
    return stck ? stck->len : 0;
}


void UnsafeStack_push(UnsafeStack* stck, void* value) {
    if (!stck) {
        return;
    }

    if (stck->len + 1 > stck->capacity) {
        size_t new_capacity = stck->capacity * 2;
        char* new_data = realloc(stck->data, new_capacity * stck->objsize);

        if (!new_data) {
            return;
        }

        stck->capacity = new_capacity;
        stck->data = new_data;
    }

    memcpy(stck->data + (stck->len * stck->objsize), value, stck->objsize);
    stck->len++;
}


void* UnsafeStack_pop(UnsafeStack* stck) {
    if (!stck || stck->len == 0) {
        return NULL;
    }

    stck->len--;
    return stck->data + (stck->len * stck->objsize);
}
