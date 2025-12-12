#include <stdio.h>

#define SIZE 10

struct item {
    int value;
    struct item *prev;
    struct item *next;
};

// todo use null pointed for ends.

int main(void) {
    struct item list[SIZE];

    for (int i = 0; i < SIZE; i++) {
        if (i == 0) {
            list[i].prev = NULL;
            list[i].next = &list[i+1];
        } else if (i == SIZE - 1) {
            list[i].next = NULL;
            list[i].prev = &list[i-1];
        } else {
            list[i].prev = &list[i-1];
            list[i].next = &list[i+1];
        }
        list[i].value = i;
    }

    struct item *block = &list[0];
    // We have a pointer to a struct so we need ->
    puts("Walk through the list:");
    while (block->next != NULL) {
        printf("%d, Ptr: %p, Prev: %p, Next: %p \n", block->value, block, block->prev, block->next);
        block = block->next;
    }
    printf("%d, Ptr: %p, Prev: %p, Next: %p \n", block->value, block, block->prev, block->next);

    puts("\nPrint the array:");
    for (int i = 0; i < SIZE; i++) {
        printf("%d, Ptr: %p, Prev: %p, Next: %p \n", list[i].value, &list[i], list[i].prev, list[i].next);
    }

}