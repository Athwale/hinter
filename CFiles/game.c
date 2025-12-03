//
// Created by omejzlik on 12/2/25.
//

#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#define WORDS 10
#define LEN 20

bool isIn(char c, ) {

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
    // todo limit to letters only
    while (c != EOF) {
        puts("Guess a letter:");
        c = getchar();
        // Clear remaining \n
        while (getchar() != '\n') {}

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
        while (chosen[i] != '\0') {
            // todo is in function?
            printf("%c", chosen[i]);
            i++;
        }

        printf("\n");
    }
}