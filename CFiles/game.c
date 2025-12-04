//
// Created by omejzlik on 12/2/25.
//

#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#define WORDS 10
#define LEN 20

bool isIn(int c, int arr[]) {
    for (int i = 0; i < 27; i++) {
        if (c == arr[i]) {
            return true;
        }
    }
    return false;
}

int main(void) {
    srand(time(NULL));

    int c = 0;
    const int r = rand() % WORDS;

    char strings[WORDS][20] = {"dog", "cat", "bird", "bear", "fish", "raptor", "wolf", "fox", "lynx", "snake"};
    char chosen[LEN];
    int abc[27];
    for (int i = 0; i < 27; i++) {
        abc[i] = 0;
    }

    for (int i = 0; i < WORDS; i++) {
        printf("Available: %s\n", strings[i]);
    }

    for (int i = 0; i < LEN; i++) {
        chosen[i] = strings[r][i];
    }

    puts(chosen);

    puts("Simple word game, input a single character and try to guess the word.");
    // todo does not work to exit

    while (c != EOF) {
        puts("Guess a letter:");
        c = getchar();
        // Clear remaining \n
        while (getchar() != '\n') {}

        // Limit to letters only
        if (c < 'a' || c > 'z') {
            puts("Invalid input");
            continue;
        }

        // Save the new char to the first free space in abc array.
        for (int i = 0; i < 27; i++) {
            if (abc[i] == c) {
                break;
            }
            if (abc[i] == 0) {
                abc[i] = c;
                break;
            }
        }

        for (int i = 0; i < 27; i++) {
            printf("%c ", abc[i]);
        }
        puts("");

        int i = 0;
        bool done = true;
        while (chosen[i] != '\0') {
            if (isIn(chosen[i], abc)) {
                printf("%c", chosen[i]);
            } else {
                printf("_");
                done = false;
            }
            i++;
        }
        printf("\n");
        if (done) {
            puts("Done");
            return 0;
        }
    }
}