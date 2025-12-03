//
// Created by omejzlik on 11/20/25.
//

# include <stdio.h>

int main(void) {

    int s = 0;

    puts("Input side length: ");
    int r = scanf("%d", &s);
    while (r != 1) {
        r = scanf("%d", &s);
        while (getchar() != '\n') {}
        puts("Wrong argument");
    }

    printf("Side length: %d\n", s);
    printf("Square size: %d\n", s*4);
    printf("Square surface: %d", s*s);

    return 0;
}
