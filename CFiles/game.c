//
// Created by omejzlik on 12/2/25.
//

#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#define WORDS 15
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
    int tries = 0;
    int hint = 0;

    printf("How many hints? > ");
    // Give it the address of the variable so it can save into it. *var accesses the value.
    // todo implement hints.
    // todo change getch to scanf and use " %c"

    char strings[WORDS][20] = {"elephant", "tiger", "bird", "bear", "fish", "raptor", "wolf", "coyote", "lynx",
        "snake", "bull", "lizard", "dinosaur", "cheetah", "toucan" };
    char chosen[LEN];
    int abc[27];
    for (int i = 0; i < 27; i++) {
        abc[i] = 0;
    }

    // Get a hint.
    scanf("%d", &hint);
    // Clearing buffer, but it can be done with a space before the scanf format. " %d"
    getchar();
    if (hint > 3) {
        puts("Nope, limiting hint to 3");
        hint = 3;
    }

    // Select a word.
    printf("Hint: ");
    for (int i = 0; i < LEN; i++) {
        chosen[i] = strings[r][i];
        if (hint > 0) {
            printf("%c", chosen[i]);
            hint--;
        }
    }
    printf("\n");

    int i = 0;
    while (chosen[i] != '\0') {
        tries++;
        i++;
    }
    tries *= 2;
    if (tries >= 10) {
        tries = 10;
    }

    puts("Simple word game, input a single character and try to guess the word.");
    // todo does not work to exit

    while (c != EOF) {
        if (tries == 0) {
            puts("You loose");
            return 1;
        }
        printf("Tries: %d\n", tries);
        printf("Guess a letter: ");
        c = getchar();
        tries--;
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
            puts("You win");
            return 0;
        }
    }
}