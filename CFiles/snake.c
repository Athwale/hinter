#include <stdio.h>
#include <ncurses.h>
#include <math.h>

// todo check sqrt and add if needed.
#define SIZE 400
#define HEAD_POS 150

// block types:
#define EMPTY 0
#define HEAD 1
#define BODY 2
#define FOOD 3

//yyyyyy
//x
//x
//x

struct block {
    int posX;
    int posY;
    int type; // 0 - empty, 1 - food, 2 - body, 3 - head
    struct block *prev;
    struct block *next;
    struct block *next_tail;
};

void print_field(struct block arr[SIZE]) {
    char c = '\0';
    for (int i = 0; i < SIZE; i++) {
        switch (arr[i].type) {
            case EMPTY:
                c = '-';
                break;
            case FOOD:
                c = '*';
                break;
            case BODY:
                c = '#';
                break;
            case HEAD:
                c = '0';
                break;
            default:
                break;
        }
        mvaddch(arr[i].posX, arr[i].posY, c);
        }
    refresh();
}

struct block *update_field(struct block *head, char direction) {
    struct block *new_head = nullptr;
    struct block *last_tail = head;
    while (last_tail->next_tail != nullptr) {
        last_tail = last_tail->next_tail;
    }

    switch (direction) {
        case 'w':
            // move the head up and shift body positions.
            head->type = BODY;
            head->prev->type = HEAD;
            new_head = head->prev;
            break;
        case 's':
            // Move the head down and shift body positions.
            // Head becomes body and the next block becomes the new head.
            head->type = BODY;
            head->next->type = HEAD;
            new_head = head->next;
            new_head->next_tail = head;
            // Last tail must become emtpy.
            last_tail->type = EMPTY;
            last_tail->next_tail = nullptr;
            break;
        case 'a':
            break;
        case 'd':
            break;
        default:
            break;
    }
    return new_head;
}

int main(void) {
    // todo make a pointer linked field

    // Init playing field.
    struct block field[SIZE];

    // Init linked list.
    int width = (int)sqrt(SIZE);
    int x = 0;
    int y = 0;

    for (int i = 0; i < SIZE; i++) {
        if (i == 0) {
            field[i].prev = nullptr;
            field[i].next = &field[i+1];
        } else if (i == SIZE - 1) {
            field[i].next = nullptr;
            field[i].prev = &field[i-1];
        } else {
            field[i].prev = &field[i-1];
            field[i].next = &field[i+1];
        }
        // All blocks are initially empty space.
        field[i].type = EMPTY;
        field[i].next_tail = nullptr;

        if (x == width) {
            y++;
            x = 0;
        }

        field[i].posX = x;
        field[i].posY = y;
        x++;
    }

    // Init snake
    struct block *head = &field[HEAD_POS];
    head->type = HEAD;
    head->next_tail = head->prev;

    head->prev->type = BODY;
    head->prev->next_tail = head->prev->prev;

    head->prev->prev->type = BODY;
    head->prev->prev->next_tail = head->prev->prev->prev;

    head->prev->prev->prev->type = BODY;
    head->prev->prev->prev->next_tail = head->prev->prev->prev->prev;

    struct block *block = &field[0];
    // We have a pointer to a struct so we need ->
    // puts("Walk through the field:");
    // while (block->next != NULL) {
    //     printf("%d, Ptr: %p, Prev: %p, Next: %p, X: %d, Y: %d \n", block->type, block, block->prev, block->next, block->posX, block->posY);
    //     block = block->next;
    // }
    // printf("%d, Ptr: %p, Prev: %p, Next: %p, X: %d, Y: %d \n", block->type, block, block->prev, block->next, block->posX, block->posY);

    initscr();
    cbreak();
    noecho();

    print_field(field);

    char c = '\0';
    while (c != 'q') {
        scanf("%c", &c);
        // todo update field and redraw.
        head = update_field(head, c);
        print_field(field);
    }

    endwin();
    // todo print results.
    printf("Done, press any key");
    getchar();

    return 0;
}