#include "helpers.h"

void colorize(int height, int width, RGBTRIPLE image[height][width])
{
    // Define the color you want to change black pixels to
    RGBTRIPLE newColor;
    newColor.rgbtBlue = 1; // Change these values to set your desired color
    newColor.rgbtGreen = 246;
    newColor.rgbtRed = 255;

    // Iterate through each pixel in the image
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            // Check if the pixel is black (all color components are 0)
            if (image[i][j].rgbtBlue == 0 && image[i][j].rgbtGreen == 0 && image[i][j].rgbtRed == 0)
            {
                // Change the color of black pixels to the new color
                image[i][j] = newColor;
            }
        }
    }
}
