import csv
import requests


def main():
    # Read NYTimes Covid Database
    download = requests.get(
        "https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-states.csv"
    )
    decoded_content = download.content.decode("utf-8")
    file = decoded_content.splitlines()
    reader = csv.DictReader(file)

    # Construct 14 day lists of new cases for each states
    new_cases = calculate(reader)

    # Create a list to store selected states
    states = []
    print("Choose one or more states to view average COVID cases.")
    print("Press enter when done.\n")

    while True:
        state = input("State: ")
        if state in new_cases:
            states.append(state)
        if len(state) == 0:
            break

    print("\nSeven-Day Averages")

    # Print out 7-day averages for this week vs last week
    comparative_averages(new_cases, states)


def calculate(reader):
    new_cases = {}  # Initialize the dictionary
    last_cases = {}  # Keep track of the last case count for each state

    for row in reader:
        state = row['state']
        cases = int(row['cases'])

        if state not in new_cases:
            new_cases[state] = [cases]
            last_cases[state] = cases
        else:
            new_cases[state].append(cases - last_cases[state])
            last_cases[state] = cases

        if len(new_cases[state]) > 14:
            new_cases[state].pop(0)
    return new_cases

# Calculate and print out seven day average for given state
def comparative_averages(new_cases, states):
    for state in states:
        new_week = sum(new_cases[state][-7:]) / 7
        prev_week = sum(new_cases[state][:7]) / 7

        try:
            percent_change = ((new_week - prev_week) / prev_week) * 100
        except ZeroDivisionError:
            percent_change = float('inf')

        increase_or_decrease = "increase" if percent_change > 0 else "decrease"

        print(f"{state} had a 7-day average of {new_week:.0f} and a {increase_or_decrease} of {abs(percent_change):.0f}%.")


if __name__ == "__main__":
    main()
