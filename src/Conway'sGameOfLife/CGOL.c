#include <stdio.h>
#include <stdlib.h>

int main() {
    int gridSize;
    printf("Grid size: ");
    scanf("%d", &gridSize);

    char currentGrid[12][12], nextGrid[12][12];
    int row, col;

    for (row = 1; row <= gridSize; ++row)
        for (col = 1; col <= gridSize; ++col)
            currentGrid[row][col] = '.';

    int liveCellCount;
    printf("Live cell num: ");
    scanf("%d", &liveCellCount);

    for (int c = 0; c < liveCellCount; ++c) {
        int x, y;
        printf("X Y: ");
        scanf("%d %d", &x, &y);
        currentGrid[x + 1][y + 1] = '#';
    }

    int gen;
    printf("Generations: ");
    scanf("%d", &gen);

    getchar();

    for (int step = 0; step < gen; ++step) {
        system("clear");
        printf("Generation %d:\n", step + 1);

        for (row = 1; row <= gridSize; ++row) {
            for (col = 1; col <= gridSize; ++col)
                printf("%c ", currentGrid[row][col]);
            printf("\n");
        }

        printf("\nPress Enter to continue...");
        getchar();

        for (row = 1; row <= gridSize; ++row) {
            for (col = 1; col <= gridSize; ++col) {
                int neighbors = 0;
                for (int dRow = -1; dRow <= 1; ++dRow)
                    for (int dCol = -1; dCol <= 1; ++dCol)
                        if (!(dRow == 0 && dCol == 0) && currentGrid[row + dRow][col + dCol] == '#')
                            neighbors++;

                if (currentGrid[row][col] == '#')
                    nextGrid[row][col] = (neighbors == 2 || neighbors == 3) ? '#' : '.';
                else
                    nextGrid[row][col] = (neighbors == 3) ? '#' : '.';
            }
        }

        for (row = 1; row <= gridSize; ++row)
            for (col = 1; col <= gridSize; ++col)
                currentGrid[row][col] = nextGrid[row][col];
    }

    system("clear");
    printf("Final Generation:\n");
    for (row = 1; row <= gridSize; ++row) {
        for (col = 1; col <= gridSize; ++col)
            printf("%c ", currentGrid[row][col]);
        printf("\n");
    }

    return 0;
}
