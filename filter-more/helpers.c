#include "helpers.h"
#include <math.h>
#include <stdint.h>
#include <string.h>

// Convert image to grayscale
void grayscale(int height, int width, RGBTRIPLE image[height][width])
{
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            // Calculate the average of red, green, and blue components
            uint8_t avg = round((image[i][j].rgbtRed + image[i][j].rgbtGreen + image[i][j].rgbtBlue) / 3.0);
            image[i][j].rgbtRed = avg;
            image[i][j].rgbtGreen = avg;
            image[i][j].rgbtBlue = avg;
        }
    }
}

// Reflect image horizontally
void reflect(int height, int width, RGBTRIPLE image[height][width])
{
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width / 2; j++)
        {
            RGBTRIPLE temp = image[i][j];
            image[i][j] = image[i][width - 1 - j];
            image[i][width - 1 - j] = temp;
        }
    }
}

// Blur image
void blur(int height, int width, RGBTRIPLE image[height][width])
{
    // Create a temporary copy of the image to avoid modifying pixels prematurely
    RGBTRIPLE temp[height][width];
    memcpy(temp, image, sizeof(RGBTRIPLE) * height * width);

    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            int sumRed = 0, sumGreen = 0, sumBlue = 0;
            int count = 0;

            // Iterate over the 3x3 box centered at (i, j)
            for (int row = i - 1; row <= i + 1; row++)
            {
                for (int col = j - 1; col <= j + 1; col++)
                {
                    if (row >= 0 && row < height && col >= 0 && col < width)
                    {
                        sumRed += temp[row][col].rgbtRed;
                        sumGreen += temp[row][col].rgbtGreen;
                        sumBlue += temp[row][col].rgbtBlue;
                        count++;
                    }
                }
            }

            // Calculate average color values and update the image
            image[i][j].rgbtRed = round((float) sumRed / count);
            image[i][j].rgbtGreen = round((float) sumGreen / count);
            image[i][j].rgbtBlue = round((float) sumBlue / count);
        }
    }
}

// Detect edges
void edges(int height, int width, RGBTRIPLE image[height][width])
{
    // Create a temporary copy of the image to avoid modifying pixels prematurely
    RGBTRIPLE temp[height][width];
    memcpy(temp, image, sizeof(RGBTRIPLE) * height * width);

    int Gx[3][3] = {{-1, 0, 1}, {-2, 0, 2}, {-1, 0, 1}};
    int Gy[3][3] = {{-1, -2, -1}, {0, 0, 0}, {1, 2, 1}};

    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            int sumRx = 0, sumRy = 0;
            int sumGx = 0, sumGy = 0;
            int sumBx = 0, sumBy = 0;

            // Iterate over the 3x3 box centered at (i, j)
            for (int row = i - 1, r = 0; row <= i + 1; row++, r++)
            {
                for (int col = j - 1, c = 0; col <= j + 1; col++, c++)
                {
                    if (row >= 0 && row < height && col >= 0 && col < width)
                    {
                        sumRx += temp[row][col].rgbtRed * Gx[r][c];
                        sumRy += temp[row][col].rgbtRed * Gy[r][c];
                        sumGx += temp[row][col].rgbtGreen * Gx[r][c];
                        sumGy += temp[row][col].rgbtGreen * Gy[r][c];
                        sumBx += temp[row][col].rgbtBlue * Gx[r][c];
                        sumBy += temp[row][col].rgbtBlue * Gy[r][c];
                    }
                }
            }

            // Calculate the magnitude of the gradient and cap it at 255
            int newRed = round(sqrt(sumRx * sumRx + sumRy * sumRy));
            int newGreen = round(sqrt(sumGx * sumGx + sumGy * sumGy));
            int newBlue = round(sqrt(sumBx * sumBx + sumBy * sumBy));

            image[i][j].rgbtRed = (newRed > 255) ? 255 : newRed;
            image[i][j].rgbtGreen = (newGreen > 255) ? 255 : newGreen;
            image[i][j].rgbtBlue = (newBlue > 255) ? 255 : newBlue;
        }
    }
}
