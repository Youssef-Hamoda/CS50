-- Keep a log of any SQL queries you execute as you solve the mystery

-- Crime Details
SELECT *
FROM crime_scene_reports
WHERE street LIKE 'Humphrey%'
AND day = 28 AND month = 7;

-- Witness Interviews
SELECT name, transcript
FROM interviews
WHERE year = 2021 AND month = 7 AND day = 28;

-- License Plate of Thief's Car
SELECT *
FROM bakery_security_logs
WHERE (year, month, day, hour) = (2021, 7, 28, 10)
AND minute > 20 AND minute < 30;

-- Names of People
SELECT *
FROM people p
JOIN bakery_security_logs bsl ON p.license_plate = bsl.license_plate
WHERE (bsl.year, bsl.month, bsl.day, bsl.hour) = (2021, 7, 28, 10)
AND bsl.minute > 15 AND bsl.minute < 30;

-- ATM Transactions
SELECT account_number
FROM atm_transactions
WHERE (year, month, day) = (2021, 7, 28)
AND transaction_type = 'withdraw'
AND atm_location LIKE 'Legget%';

-- Name of Thief and Phone Number of Accomplice
SELECT p.id, p.name, pc.caller, pc.receiver
FROM people p
JOIN phone_calls pc ON pc.caller = p.phone_number
JOIN bank_accounts ba ON p.id = ba.person_id
JOIN bakery_security_logs bsl ON p.license_plate = bsl.license_plate
WHERE (bsl.year, bsl.month, bsl.day, bsl.hour) = (2021, 7, 28, 10)
AND bsl.minute > 15 AND bsl.minute < 30
AND ba.account_number IN (
    SELECT account_number
    FROM atm_transactions
    WHERE (year, month, day) = (2021, 7, 28)
    AND transaction_type = 'withdraw'
    AND atm_location LIKE 'Legget%'
)
AND (pc.year, pc.month, pc.day) = (2021, 7, 28)
AND pc.duration < 60;

-- Name of Accomplice
SELECT *
FROM people
WHERE phone_number = '(375) 555-8161';

-- Destination
SELECT f.destination_airport_id, a.city
FROM flights f
JOIN airports a ON f.destination_airport_id = a.id
JOIN passengers p ON f.id = p.flight_id
WHERE p.passport_number = (
    SELECT passport_number
    FROM people
    WHERE name = 'Bruce'

)
AND (f.year, f.month, f.day) = (2021, 7, 29);

