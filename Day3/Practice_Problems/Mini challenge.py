# Mini Challenge: Number Analysis Tool

def number_analysis():
    num = int(input("Enter a number: "))
    original = num
    num = abs(num)

    # even or odd
    even_odd_result = "Even" if num % 2 == 0 else "Odd"

    # prime check
    if num < 2:
        prime_result = "Not Prime"
    else:
        prime_result = "Prime"
        for i in range(2, int(num ** 0.5) + 1):
            if num % i == 0:
                prime_result = "Not Prime"
                break

    # digit count + reverse (using the same loop for both)
    digit_count = 0
    reversed_num = 0
    temp = num
    while temp > 0:
        digit = temp % 10
        reversed_num = (reversed_num * 10) + digit
        temp = temp // 10
        digit_count += 1
    if digit_count == 0:
        digit_count = 1

    # palindrome check
    palindrome_result = "Yes" if num == reversed_num else "No"

    # display
    print("\n----- Number Analysis Report -----")
    print(f"Number Entered      : {original}")
    print(f"Even or Odd          : {even_odd_result}")
    print(f"Prime Check          : {prime_result}")
    print(f"Digit Count          : {digit_count}")
    print(f"Reversed Number      : {reversed_num}")
    print(f"Palindrome           : {palindrome_result}")
    print("-----------------------------------\n")


number_analysis()