#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

#include "wav.h"

int check_format(WAVHEADER header);
int get_block_size(WAVHEADER header);

int main(int argc, char *argv[])
{
    // Ensure proper usage
    if (argc != 3)
    {
        printf("Usage: %s input.wav output.wav\n", argv[0]);
        return 1;
    }

    // Open input file for reading
    FILE *input_file = fopen(argv[1], "r");
    if (input_file == NULL)
    {
        printf("Could not open %s for reading.\n", argv[1]);
        return 1;
    }

    // Read header
    WAVHEADER header;
    fread(&header, sizeof(WAVHEADER), 1, input_file);

    // Use check_format to ensure WAV format
    if (!check_format(header))
    {
        printf("Input is not a WAV file.\n");
        fclose(input_file);
        return 1;
    }

    // Open output file for writing
    FILE *output_file = fopen(argv[2], "w");
    if (output_file == NULL)
    {
        printf("Could not open %s for writing.\n", argv[2]);
        fclose(input_file);
        return 1;
    }

    // Write header to file
    fwrite(&header, sizeof(WAVHEADER), 1, output_file);

    // Use get_block_size to calculate size of block
    int block_size = get_block_size(header);

    // Write reversed audio to file
    BYTE *buffer = malloc(block_size);
    if (buffer == NULL)
    {
        printf("Memory allocation error.\n");
        fclose(input_file);
        fclose(output_file);
        return 1;
    }

    fseek(input_file, 0, SEEK_END);
    long file_size = ftell(input_file);
    fseek(input_file, sizeof(WAVHEADER), SEEK_SET);
    fseek(input_file, 0, SEEK_END);

    while (file_size > sizeof(WAVHEADER))
    {
        fseek(input_file, -block_size, SEEK_CUR);
        fread(buffer, block_size, 1, input_file);
        fseek(input_file, -block_size, SEEK_CUR);
        fwrite(buffer, block_size, 1, output_file);
        file_size -= block_size;
    }

    // Clean up
    free(buffer);
    fclose(input_file);
    fclose(output_file);
}

int check_format(WAVHEADER header)
{
    return (header.chunkID[0] == 'R' && header.chunkID[1] == 'I' && header.chunkID[2] == 'F' && header.chunkID[3] == 'F' &&
            header.format[0] == 'W' && header.format[1] == 'A' && header.format[2] == 'V' && header.format[3] == 'E');
}

int get_block_size(WAVHEADER header)
{
    return header.numChannels * (header.bitsPerSample / 8);
}
