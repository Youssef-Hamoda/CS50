#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(int argc, char *argv[])
{
    // Check for command line args
    if (argc != 2)
    {
        printf("Usage: ./read infile\n");
        return 1;
    }

    // Create buffer to read into
    char buffer[7];

    // Create array to store plate numbers
    char *plates[8];

    FILE *infile = fopen(argv[1], "r");

    int idx = 0;

    while (fread(buffer, 1, 7, infile) == 7)
    {
        // Allocate memory for each plate
        if (plates[idx] == NULL)
        {
            printf("Memory allocation error.\n");
            return 2;
        }
        
        // Replace '\n' with '\0'
        buffer[6] = '\0';

        // Copy buffer into the allocated memory
        strncpy(plates[idx], buffer, 7); // Copy 7 bytes from buffer to plates[idx]

        idx++;
    }

    // Close the file after reading
    fclose(infile);

    // Print the stored license plates
    for (int i = 0; i < 8; i++)
    {
        printf("%s\n", plates[i]);

        // Free the allocated memory for each plate
        free(plates[i]);
    }
}
