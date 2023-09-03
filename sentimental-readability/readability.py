from cs50 import get_string


def main():
    text = get_string("Text: ")

    num_letters = count_letters(text)
    num_words = count_words(text)
    num_sentences = count_sentences(text)

    L = (num_letters / num_words) * 100
    S = (num_sentences / num_words) * 100
    index = round(0.0588 * L - 0.296 * S - 15.8)

    if index >= 16:
        print("Grade 16+")
    elif index < 1:
        print("Before Grade 1")
    else:
        print(f"Grade {index}")


def count_letters(text):
    count = 0
    for char in text:
        if char.isalpha():
            count += 1
    return count


def count_words(text):
    return len(text.split())


def count_sentences(text):
    count = 0
    for char in text:
        if char in [".", "!", "?"]:
            count += 1
    return count


if __name__ == "__main__":
    main()
