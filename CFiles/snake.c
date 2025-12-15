#include <stdio.h>
#include <ncurses.h>
#include <math.h>
#include <time.h>
#include <stdlib.h>

// todo check sqrt and add if needed.
#define SIZE 40
#define HEAD_POS 20
#define WIN_LENGTH 10
#define START_LENGTH 3

// block types:
#define EMPTY '-'
#define BODY '$'
#define FOOD '*'

//  y y y
// x
// x
// x

struct block {
    int posX;
    int posY;
    char type;
};

void print_field(char arr[SIZE][SIZE]) {
    for (int i = 0; i < SIZE; i++) {
        for (int j = 0; j < SIZE; j++) {
            mvaddch(i, j, arr[i][j]);
        }
    }
    refresh();
}

void process_move(struct block snake[], char direction, int length) {
    // Update the snake array with new coordinates.
    // todo implement boundaries.
    // Take first element, back up coords, move it, put original coord to next element.
    int prev_x = 0;
    int prev_y = 0;

    for (int i = 0; i < length; i++) {
        if (i == 0) {
            prev_x = snake[i].posX;
            prev_y = snake[i].posY;
            switch (direction) {
                case 'w':
                    snake[i].posX -= 1;
                    break;
                case 's':
                    snake[i].posX += 1;
                    break;
                case 'a':
                    snake[i].posY -= 1;
                    break;
                case 'd':
                    snake[i].posY += 1;
                    break;
                default:
                    break;
            }
        } else {
            int current_x = snake[i].posX;
            int current_y = snake[i].posY;
            snake[i].posX = prev_x;
            snake[i].posY = prev_y;
            prev_x = current_x;
            prev_y = current_y;
        }
    }
}

void update_field(char arr[SIZE][SIZE], struct block snake[], int length) {
    int x = 0;
    int y = 0;
    char type = '\0';

    // Zero the whole field.
    for (int i = 0; i < SIZE; i++) {
        for (int j = 0; j < SIZE; j++) {
            arr[i][j] = EMPTY;
        }
    }

    // Draw snake into the field.
    for (int i = 0; i < length; i++) {
        x = snake[i].posX;
        y = snake[i].posY;
        type = snake[i].type;
        // Update field blocks.
        arr[x][y] = type;
    }
}

int main(void) {
    srand(time(nullptr));
    // Init playing field.
    char field[SIZE][SIZE];
    struct block snake[WIN_LENGTH];
    int length = START_LENGTH;
    int food_x = rand() % SIZE;
    int food_y = rand() % SIZE;

    // Init field.
    for (int i = 0; i < SIZE; i++) {
        for (int j = 0; j < SIZE; j++) {
            field[i][j] = EMPTY;
        }
    }

    // Init snake
    for (int i = 0; i < length; i++) {
        snake[i].type = BODY;
        snake[i].posX = HEAD_POS;
        snake[i].posY = HEAD_POS + i;
    }

    initscr();
    cbreak();
    noecho();

    // Draw initial play area.
    update_field(field, snake, length);
    // Place food.
    field[food_x][food_y] = FOOD;
    print_field(field);

    char c = '\0';
    while (c != 'q') {
        scanf("%c", &c);
        process_move(snake, c, length);
        update_field(field, snake, length);
        print_field(field);
    }

    endwin();
    // todo print results.
    printf("Done, press any key");
    getchar();

    return 0;
}