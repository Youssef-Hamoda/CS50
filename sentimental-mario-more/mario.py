def main():
    height = get_height()

    for i in range(height):
        print(" " * (height - i - 1), end="")
        print("#" * (i + 1), end="")
        print("  ", end="")
        print("#" * (i + 1))


def get_height():
    while True:
        try:
            height = int(input("Height: "))
            if 1 <= height <= 8:
                return height
            else:
                print("Height must be between 1 and 8")
        except ValueError:
            print("Invalid input. Please enter a positive integer.")


if __name__ == "__main__":
    main()
