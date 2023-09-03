from cs50 import get_int


def main():
    card_number = get_card_number()

    num = card_number
    sum = 0
    count = 0

    while num > 0:
        if count % 2 == 0:
            sum += num % 10
        else:
            digit = 2 * (num % 10)
            sum += digit // 10 + digit % 10
        num //= 10
        count += 1

    if sum % 10 == 0:
        if (count == 13 or count == 16) and (
            card_number // 1000000000000 == 4 or card_number // 1000000000000000 == 4
        ):
            print("VISA")
        elif count == 16 and 51 <= card_number // 100000000000000 <= 55:
            print("MASTERCARD")
        elif count == 15 and (
            card_number // 10000000000000 == 34 or card_number // 10000000000000 == 37
        ):
            print("AMEX")
        else:
            print("INVALID")
    else:
        print("INVALID")


def get_card_number():
    while True:
        try:
            card_number = get_int("Number: ")
            if card_number > 0:
                return card_number
        except ValueError:
            pass


if __name__ == "__main__":
    main()
