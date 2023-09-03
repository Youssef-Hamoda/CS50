#include <cs50.h>
#include <stdio.h>

int main(void)
{
    long card_number;

    // Prompt user for a credit card number
    do
    {
        card_number = get_long("Number: ");
    }
    while (card_number <= 0);

    // Calculate the checksum
    long num = card_number;
    int sum = 0;
    int count = 0;

    while (num > 0)
    {
        if (count % 2 == 0)
        {
            sum += num % 10;
        }
        else
        {
            int digit = 2 * (num % 10);
            sum += digit / 10 + digit % 10;
        }
        num /= 10;
        count++;
    }

    // Check if the card is valid and determine the card type
    if (sum % 10 == 0)
    {
        if ((count == 13 || count == 16) && (card_number / 1000000000000 == 4 || 000card_number / 1000000000000 == 4))
        {
            printf("VISA\n");
        }
        else if (count == 16 && card_number / 100000000000000 >= 51 && card_number / 100000000000000 <= 55)
        {
            printf("MASTERCARD\n");
        }
        else if (count == 15 && (card_number / 10000000000000 == 34 || card_number / 10000000000000 == 37))
        {
            printf("AMEX\n");
        }
        else
        {
            printf("INVALID\n");
        }
    }
    else
    {
        printf("INVALID\n");
    }

    return 0;
}