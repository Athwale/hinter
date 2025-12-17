#include <stdio.h>
#include <ncurses.h>
#include <math.h>
#include <time.h>
#include <stdlib.h>
#include <poll.h>
#include <unistd.h>

// todo check sqrt and add if needed.
#define SIZE 40
#define HEAD_POS 20
#define WIN_LENGTH 10
#define START_LENGTH 3
#define SPEED 200

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

bool process_move(struct block snake[], char direction, int length, int food_x, int food_y) {
    // Update the snake array with new coordinates.
    // todo implement boundaries.
    // todo implement inability to 180 move
    // todo implement winning
    // todo implement biting yourself.
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
    // Check if food was consumed
    if (snake[0].posX == food_x && snake[0].posY == food_y) {
        return true;
    }
    return false;
}

void update_field(char arr[SIZE][SIZE], struct block snake[], int length, int food_x, int food_y) {
    // Zero the whole field.
    for (int i = 0; i < SIZE; i++) {
        for (int j = 0; j < SIZE; j++) {
            arr[i][j] = EMPTY;
        }
    }

    // Place food.
    arr[food_x][food_y] = FOOD;

    // Draw snake into the field.
    for (int i = 0; i < length; i++) {
        arr[snake[i].posX][snake[i].posY] = snake[i].type;
    }
}

char get_input(char current) {
    struct pollfd mypoll = {STDIN_FILENO, POLLIN|POLLPRI};
    char c;
    if( poll(&mypoll, 1, SPEED) )    {
        scanf("%c", &c);
        return c;
    }
    return current;
}

int main(void) {
    // Init rand function.
    srand(time(nullptr));

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

    // Init ncurses.
    initscr();
    cbreak();
    noecho();

    // Draw initial play area.
    update_field(field, snake, length, food_x, food_y);
    print_field(field);

    // Main loop.
    char last_direction = 's';
    char c = 'w';
    bool food_consumed = false;

    while (c != 'q') {
        c = get_input(c);
        if (c == 'w' && last_direction == 's') {
            c = 's';
        }
        if (c == 's' && last_direction == 'w') {
            c = 'w';
        }
        if (c == 'a' && last_direction == 'd') {
            c = 'd';
        }
        if (c == 'd' && last_direction == 'a') {
            c = 'a';
        }
        last_direction = c;

        food_consumed = process_move(snake, c, length, food_x, food_y);
        if (food_consumed) {
            // Grow snake. The new block will be added to the correct place on the next move.
            snake[length].posX = snake[0].posX;
            snake[length].posY = snake[0].posY;
            snake[length].type = BODY;
            length += 1;

            // New food location.
            food_x = rand() % SIZE;
            food_y = rand() % SIZE;
        }
        update_field(field, snake, length, food_x, food_y);
        print_field(field);
    }

    endwin();
    // todo print results.
    printf("Done, press any key");
    getchar();

    return 0;
}