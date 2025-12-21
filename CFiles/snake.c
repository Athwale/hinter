#include <stdio.h>
#include <ncurses.h>
#include <math.h>
#include <time.h>
#include <stdlib.h>
#include <poll.h>
#include <string.h>
#include <unistd.h>

// todo check sqrt and add if needed.
#define SIZE 40
#define HEAD_POS 20
#define WIN_LENGTH 15
#define START_LENGTH 10
#define SPEED 100

// block types:
#define EMPTY '.'
#define BODY '0'
#define FOOD '#'

// clear; cc snake.c -o snake -lncurses; ./snake
//  y y y
// x
// x
// x

struct block {
    int posX;
    int posY;
    char type;
};

bool print_field(char arr[SIZE][SIZE], int length, bool ate);
int process_move(struct block snake[], char direction, int length, int food_x, int food_y);
void update_field(char arr[SIZE][SIZE], struct block snake[], int length, int food_x, int food_y);
char get_input(char current);

bool print_field(char arr[SIZE][SIZE], int length, bool ate) {
    int body_parts = 0;

    for (int i = 0; i < SIZE; i++) {
        for (int j = 0; j < SIZE; j++) {
            mvaddch(i, j, arr[i][j]);
            if (arr[i][j] == BODY)
                body_parts++;
        }
    }
    addstr("\nMovement, WSAD, Q-Quit, P-Pause");
    char score[40];
    snprintf(score, sizeof(score), "\nScore: %d\n", length);
    addstr(score);
    refresh();

    if (length > body_parts) {
        // We bit ourselves because there are less body parts than the length of the snake.
        // If the snake eats the new part is added on the next move, so we have to ignore it.
        if (ate) {
            return false;
        }
        return true;
    }
    // Normal step, nothing happened, move on.
    return false;
}

int process_move(struct block snake[], char direction, int length, int food_x, int food_y) {
    // Returns: 1 - no food, consumed, 2 - food consumed, 3 - death.

    // Update the snake array with new coordinates.
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
                    if (snake[0].posX == -1) {
                        return 3;
                    }
                    break;
                case 's':
                    snake[i].posX += 1;
                    if (snake[0].posX == SIZE) {
                        return 3;
                    }
                    break;
                case 'a':
                    snake[i].posY -= 1;
                    if (snake[0].posY == -1) {
                        return 3;
                    }
                    break;
                case 'd':
                    snake[i].posY += 1;
                    if (snake[0].posY == SIZE) {
                        return 3;
                    }
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

    char pos[20];
    snprintf(pos, sizeof(pos), "\nHead pos: x:%d y:%d\n", snake[0].posX, snake[0].posY);
    addstr(pos);

    // Check if food was consumed
    if (snake[0].posX == food_x && snake[0].posY == food_y) {
        return 2;
    }
    return 1;
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
    char inputs[] = "wsadqp";
    char c;

    if (poll(&mypoll, 1, SPEED))    {
        scanf("%c", &c);
        for (int i = 0; i < strlen(inputs); i++) {
            if (c == inputs[i]) {
                return c;
            }
        }
    }
    return current;
}

void end_game(bool win, int length) {
    endwin();
    if (!win) {
        puts("You died.");
    } else if (length == WIN_LENGTH) {
        puts("You win.");
    }

    printf("Snake length %d\n", length);
    puts("Done, press any key");
    getchar();
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
    print_field(field, length, false);

    // Main loop.
    char last_direction = 's';
    char c = 'w';
    int result = 0;
    bool paused = true;

    while (c != 'q') {
        c = get_input(c);
        if (c == 'p') {
            paused = !paused;
            c = last_direction;
        }

        if (paused) {
            continue;
        }

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

        result = process_move(snake, c, length, food_x, food_y);
        // 1 - normal step, 2 - food consumed, 3 - death by hitting the edge.

        if (result == 2) {
            // Grow snake. The new block will be added to the correct place on the next move.
            snake[length].posX = snake[0].posX;
            snake[length].posY = snake[0].posY;
            snake[length].type = BODY;
            length += 1;

            if (length == WIN_LENGTH) {
                break;
            }

            // New food location.
            food_x = rand() % SIZE;
            food_y = rand() % SIZE;
        }
        update_field(field, snake, length, food_x, food_y);
        if (print_field(field, length, ((result == 2) ? true : false ))) {
            // Returns true if the snake bit itself.
            result = 3;
        }

        if (result == 3) {
            // Die.
            break;
        }
    }

    if (result == 3) {
        end_game(false, length);
    } else {
        end_game(true, length);
    }

    return 0;
}