# Loops:

#   1. Print numbers from 1 to 100.
#   2. Print all even numbers from 1 to 100.
#   3. Calculate the sum of numbers from 1 to N.
#   4. Print the multiplication table of a given number.
#   5. Count the number of digits in a number.


# 1: Print numbers from 1 to 100.
def print_1_to_100():
    for i in range(1, 101):
        print(i)


# 2: Print all even numbers from 1 to 100.
def print_even_1_to_100():
    for i in range(2, 101, 2):
        print(i)


# 3: Calculate the sum of numbers from 1 to N.
def sum_1_to_n():
    n = int(input("Enter N: "))
    total = 0
    for i in range(1, n + 1):
        total += i
    print(f"Sum from 1 to {n} is {total}")


# 4: Print the multiplication table of a given number.
def multiplication_table():
    num = int(input("Enter a number: "))
    for i in range(1, 11):
        print(f"{num} x {i} = {num * i}")


# 5: Count the number of digits in a number.
def count_digits():
    num = int(input("Enter a number: "))
    num = abs(num)
    count = 0
    while num > 0:
        num = num // 10
        count += 1
    if count == 0:
        count = 1
    print(f"Number of digits: {count}")

tasks = {
    "1": print_1_to_100,
    "2": print_even_1_to_100,
    "3": sum_1_to_n,
    "4": multiplication_table,
    "5": count_digits
}

def menu():
    while True:
        print("1: Print 1 to 100")
        print("2: Print Even 1 to 100")
        print("3: Sum 1 to N")
        print("4: Multiplication Table")
        print("5: Count Digits")
        print("0: Exit")
        choice = input("Enter your choice: ")

        if choice == "0":
            break
        elif choice in tasks:
            tasks[choice]()
        else:
            print("Invalid choice, try again.")


menu()