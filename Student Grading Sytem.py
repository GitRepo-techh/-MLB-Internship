# Build a Student Grading System that takes student name, class, subjects, and marks as input, calculates the average, and assigns grades (A, B, C, F). You can use grading criteria by yourself.
student_name = input("Enter your name:")
student_class = input("Enter your class:")
subjects = int(input("Enter your total subjects:"))

def calculate_individual_grade():

    

    total_marks = 0

    for i in range(subjects):
    
      enter_subject = input("Enter your subject:  ")
      enter_marks = int(input("Enter your marks in this subject:"))
      enter_total_marks = int(input("Enter total marks in this subject:"))

    # To calculate the grade of the student based on the marks obtained in each subject.

      if enter_marks == (0.9 * enter_total_marks):
            print("Your Grade is A")
      elif enter_marks >= (0.75 * enter_total_marks):
            print("Your Grade is B")
      elif enter_marks >= (0.5 * enter_total_marks):
            print("Your Grade is C")
      elif  enter_marks >= (0.25 * enter_total_marks):
            print("Your Grade is D")
      else:
            print("You fail.")

      total_marks += enter_marks
    average_marks = total_marks/subjects
    return total_marks, average_marks


def average_grade(total_marks, average_marks):

    #A function to calculate the average grade of the student based on the average marks obtained in all subjects.

   

    if average_marks >= (0.9 * total_marks):
     return "Your Grade is A"
    elif  average_marks >= (0.75 * total_marks):
     return "Your Grade is B"   
    elif  average_marks >= (0.5 * total_marks):
     return "Your Grade is C"
    elif  average_marks >= (0.25 * total_marks):
     return "Your Grade is D"
    else:
     return "You fail."


total_marks, average_marks = calculate_individual_grade()   
print(f"Student Name: {student_name}")
print(f"Class: {student_class}")
print(f"Total Marks: {total_marks}")
print(f"Average Marks: {average_marks}")
print(average_grade(total_marks, average_marks))