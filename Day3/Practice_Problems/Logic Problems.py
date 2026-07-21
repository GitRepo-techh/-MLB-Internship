# Logic Building Problems:

#   1. Reverse a number.
#   2. Check whether a number is a palindrome.
#   3. Generate the Fibonacci sequence.
#   4. Check whether a number is prime.
#   5. Find all prime numbers between 1 and 100.


# 1: Reverse a number.
def reverse_number():
    num = int(input("Enter a number: "))
    num = abs(num)
    reversed_num = 0
    while num > 0:
        digit = num % 10
        reversed_num = (reversed_num * 10) + digit
        num = num // 10
    print(f"Reversed number: {reversed_num}")


# 2: Check whether a number is a palindrome.
def is_palindrome():
    num = int(input("Enter a number: "))
    original = num
    num = abs(num)
    reversed_num = 0
    while num > 0:
        digit = num % 10
        reversed_num = (reversed_num * 10) + digit
        num = num // 10
    if original == reversed_num:
        print(f"{original} is a palindrome.")
    else:
        print(f"{original} is not a palindrome.")


# 3: Generate the Fibonacci sequence.
def fibonacci():
    n = int(input("Enter how many terms: "))
    a, b = 0, 1
    for _ in range(n):
        print(a, end=" ")
        a, b = b, a + b
    print()


# 4: Check whether a number is prime.
def is_prime():
    num = int(input("Enter a number: "))
    if num < 2:
        print(f"{num} is not a prime number.")
        return
    for i in range(2, int(num ** 0.5) + 1):
        if num % i == 0:
            print(f"{num} is not a prime number.")
            return
    print(f"{num} is a prime number.")


# 5: Find all prime numbers between 1 and 100.
def primes_1_to_100():
    for num in range(2, 101):
        is_prime = True
        for i in range(2, int(num ** 0.5) + 1):
            if num % i == 0:
                is_prime = False
                break
        if is_prime:
            print(num, end=" ")
    print()

# menu of a dictionary maps user choice (string) to the function to call, then menu() loops and calls it

tasks = {
    "1": reverse_number,
    "2": is_palindrome,
    "3": fibonacci,
    "4": is_prime,
    "5": primes_1_to_100
}

def menu():
    while True:
        print("1: Reverse a Number")
        print("2: Check Palindrome")
        print("3: Fibonacci Sequence")
        print("4: Check Prime")
        print("5: Primes 1 to 100")
        print("0: Exit")
        choice = input("Enter your choice: ")

        if choice == "0":
            break
        elif choice in tasks:
            tasks[choice]()
        else:
            print("Invalid choice, try again.")


menu()