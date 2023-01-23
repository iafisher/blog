#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>


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
