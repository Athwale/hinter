#include <stdio.h>
#include <ncurses.h>

#define SIZE_X 20
#define SIZE_Y 20

struct block {
    int posX;
    int posY;
    int type; // 0 - empty, 1 - food, 2 - body, 3 - head
};

void print_field(struct block arr[SIZE_X][SIZE_Y]) {
    char c = '\0';
    for (int i = 1; i < SIZE_Y; i++) {
        for (int j = 1; j < SIZE_X; j++) {
            switch (arr[i][j].type) {
                case 0:
                    // Empty
                    c = '-';
                    break;
                case 1:
                    // Food
                    c = '*';
                    break;
                case 2:
                    // Body
                    c = '#';
                    break;
                case 3:
                    // Head
                    c = 'O';
                    break;
            }
            mvaddch(arr[i][j].posX, arr[i][j].posY, c);
        }
    }
    refresh();
}

void update_part(struct block element, char direction) {
    switch (direction) {

    }
}

void update_field(struct block arr[SIZE_X][SIZE_Y], char key) {
    for (int i = 0; i < SIZE_Y; i++) {
        for (int j = 0; j < SIZE_X; j++) {
            if (arr[i][j].type == 3 || arr[i][j].type == 2) {
                // Update the head.
                update_part(arr[i][j], key);
            }
        }
    }
}

int main(void) {
    // todo switch to pointers for practice?

    // Init playing field.
    struct block field[SIZE_X][SIZE_Y];

    for (int i = 1; i < SIZE_Y; i++) {
        for (int j = 1; j < SIZE_X; j++) {
            field[i][j].posX = i;
            field[i][j].posY = j;
            field[i][j].type = 0;
        }
    }
    // Init snake.
    field[10][5].type = 2;
    field[10][6].type = 2;
    field[10][7].type = 3;

    initscr();
    cbreak();
    noecho();

    print_field(field);

    char c = '\0';
    while (c != 'q') {
        scanf("%c", &c);
        // todo update field and redraw.
        update_field(field, c);
        print_field(field);
    }

    endwin();
    // todo print results.
    printf("Done, press any key");
    getchar();

    return 0;
}