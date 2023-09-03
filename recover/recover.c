#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

#define BLOCK_SIZE 512

typedef uint8_t BYTE;

int main(int argc, char *argv[])
{
    // Check command-line arguments
    if (argc != 2)
    {
        fprintf(stderr, "Usage: %s IMAGE\n", argv[0]);
        return 1;
    }

    // Open forensic image
    FILE *file = fopen(argv[1], "r");
    if (file == NULL)
    {
        fprintf(stderr, "Could not open %s for reading\n", argv[1]);
        return 1;
    }

    BYTE buffer[BLOCK_SIZE];
    int jpeg_counter = 0;
    FILE *jpeg = NULL;

    while (fread(buffer, 1, BLOCK_SIZE, file) == BLOCK_SIZE)
    {
        // Check for start of a new JPEG
        if (buffer[0] == 0xff && buffer[1] == 0xd8 && buffer[2] == 0xff && (buffer[3] & 0xf0) == 0xe0)
        {
            // Close previous JPEG if one is open
            if (jpeg != NULL)
            {
                fclose(jpeg);
            }

            // Create new JPEG filename
            char filename[8];
            sprintf(filename, "%03i.jpg", jpeg_counter);

            // Open new JPEG for writing
            jpeg = fopen(filename, "w");
            if (jpeg == NULL)
            {
                fclose(file);
                fprintf(stderr, "Could not create %s\n", filename);
                return 1;
            }

            jpeg_counter++;
        }

        // Write data to JPEG if one is open
        if (jpeg != NULL)
        {
            fwrite(buffer, 1, BLOCK_SIZE, jpeg);
        }
    }

    // Close any remaining files
    if (jpeg != NULL)
    {
        fclose(jpeg);
    }
    fclose(file);

    return 0;
}
