# Conditional Statements:

#   1. Check whether a number is positive, negative, or zero.
#   2. Check whether a number is even or odd.
#   3. Create a grade calculator based on marks.
#   4. Find the largest among three numbers.
#   5. Check whether a year is a leap year.


# 1:Check whether a number is positive, negative, or zero.

def integer():
    user = int(input("Plz enter a number: "))
    if user > 0:
        print(f"{user} is a positive integer")
    elif user < 0:
        print(f"{user} is a negative integer")
    else:
        print(0)


# 2: Check whether a number is even or odd.
def even_odd():
    user = int(input("Plz enter a number: ")) 

    if user % 2 == 0:
        print(f"{user} is an even number.")
    else:
        print(f"{user} is an odd number.")


# 3: Create a grade calculator based on marks.
def Grade_cal():
    enter_marks = int(input("Enter your marks:"))
    enter_total_marks = int(input("Enter total marks:"))

    if enter_marks <= enter_total_marks:
        if enter_marks >= (0.9 * enter_total_marks):
                print("Your Grade is A")
        elif enter_marks >= (0.75 * enter_total_marks):
                print("Your Grade is B")
        elif enter_marks >= (0.5 * enter_total_marks):
                print("Your Grade is C")
        elif  enter_marks >= (0.25 * enter_total_marks):
                print("Your Grade is D")    
                print("")
        else:
                print("You fail.")
    else:
         print("PLZ enter the correct marks.")


# 4: Find the largest among three numbers.
def lar_num():
     first_num = input("Enter the first number:")
     second_num = input("Enter the second number:")
     third_num = input("Enter the third number:")

     if first_num > second_num and first_num > third_num:
          print(f"{first_num} is the greatest number of all of these.")
     elif second_num > first_num and second_num > third_num:
          print(f"{second_num} is the greatest number of all of these.")
     elif first_num == second_num and first_num > third_num:
        print(f"{first_num} is the greatest number of all of these.")
     elif second_num == third_num and second_num > first_num:
         print(f"{second_num} is the greatest number of all of these.") 
     elif first_num == third_num and first_num > second_num:
         print(f"{first_num} is the greatest number of all of these.")
     elif first_num == second_num and first_num < third_num:
         print(f"{third_num} is the greatest number of all of these.")
     elif second_num == third_num and second_num < first_num:
            print(f"{first_num} is the greatest number of all of these.")
     elif first_num == second_num == third_num:
          print(f"All numbers are the same and hence {first_num} is the greatest number.")
     else:
          print(f"{third_num} is the greatest number of all of these.")


# 5: Check whether a year is a leap year.
def is_leap_year():
  user = int(input("Enter a year: "))
  if user % 400 == 0:
    print(f"{user} is a leap year.")
  elif user % 100 == 0:
    print(f"{user} is not a leap year.")
  elif user % 4 == 0:
    print(f"{user} is a leap year.")
  else:
    return False


# menu of a dictionary maps user choice (string) to the function to call, then menu() loops and calls it
tasks = {
    "1": integer,
    "2": even_odd,
    "3": Grade_cal,
    "4": lar_num,
    "5": is_leap_year
}

def menu():
    while True:
        print("1: Positive/Negative/Zero \n")
        print("2: Even/Odd \n")
        print("3: Grade Calculator \n")
        print("4: Largest of Three \n")
        print("5: Leap Year Check \n")
        print("0: Exit")
        choice = input("Enter your choice: ")

        if choice == "0":
            break
        elif choice in tasks:
            tasks[choice]()
        else:
            print("Invalid choice, try again.")


menu()