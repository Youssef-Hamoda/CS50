#include <cs50.h>
#include <stdio.h>

int main(void)
{
    int height;

    // Prompt user for a positive integer between 1 and 8
    do
    {
        height = get_int("Height: ");
    }
    while (height < 1 || height > 8);

    // Loop through each row
    for (int i = 0; i < height; i++)
    {
        // Print spaces for the left pyramid
        for (int j = 0; j < height - i - 1; j++)
        {
            printf(" ");
        }

        // Print hashes for the left pyramid
        for (int j = 0; j <= i; j++)
        {
            printf("#");
        }

        // Print gap between pyramids
        printf("  ");

        // Print hashes for the right pyramid
        for (int j = 0; j <= i; j++)
        {
            printf("#");
        }

        // Move to the next line for the next row
        printf("\n");
    }
}