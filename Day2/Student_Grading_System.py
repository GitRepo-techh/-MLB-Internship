students = []

def get_non_empty_input(prompt):
    """Keep asking until the user enters something other than blank/whitespace."""
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("This field cannot be empty. Please try again.")


def get_valid_age(prompt):
    """Keep asking until the user enters a whole number in a sane age range."""
    while True:
        value = input(prompt).strip()
        if not value.isdigit():
            print("Age must be a number. Please try again.")
            continue
        age = int(value)
        if age <= 0 or age > 100:
            print("Please enter a realistic age (1-100).")
            continue
        return age


def roll_number_exists(roll_number):
    return any(student["Roll Number"] == roll_number for student in students)


def add_student():
    name = get_non_empty_input("Enter name: ")

    while True:
        roll_number = get_non_empty_input("Enter roll number: ")
        if roll_number_exists(roll_number):
            print("A student with this roll number already exists. Please use a different one.")
            continue
        break

    age = get_valid_age("Enter age: ")
    course = get_non_empty_input("Enter course: ")

    student = {
        "Name": name,
        "Roll Number": roll_number,
        "Age": age,
        "Course": course
    }
    students.append(student)
    print(f"\nStudent '{name}' added successfully.\n")


def view_students():
    if not students:
        print("\nNo students found.\n")
        return

    print("\n--- All Students ---")
    for student in students:
        print(f"Roll No: {student['Roll Number']} | Name: {student['Name']} | Age: {student['Age']} | Course: {student['Course']}")
    print()


def search_student():
    roll_number = input("Enter roll number to search: ").strip()

    for student in students:
        if student["Roll Number"] == roll_number:
            print("\n--- Student Found ---")
            print(f"Name: {student['Name']}")
            print(f"Roll Number: {student['Roll Number']}")
            print(f"Age: {student['Age']}")
            print(f"Course: {student['Course']}\n")
            return

    print("\nStudent not found.\n")


def update_student():
    roll_number = input("Enter roll number to update: ").strip()

    for student in students:
        if student["Roll Number"] == roll_number:
            print("Leave blank to keep current value.")

            name = input(f"New name ({student['Name']}): ").strip()
            age_input = input(f"New age ({student['Age']}): ").strip()
            course = input(f"New course ({student['Course']}): ").strip()

            if name:
                student["Name"] = name
            if age_input:
                if age_input.isdigit() and 0 < int(age_input) <= 100:
                    student["Age"] = int(age_input)
                else:
                    print("Invalid age entered - keeping the previous age.")
            if course:
                student["Course"] = course

            print("\nStudent updated successfully.\n")
            return

    print("\nStudent not found.\n")


def delete_student():
    roll_number = input("Enter roll number to delete: ").strip()

    for index, student in enumerate(students):
        if student["Roll Number"] == roll_number:
            removed_name = student["Name"]
            del students[index]
            print(f"\nStudent '{removed_name}' deleted successfully.\n")
            return

    print("\nStudent not found.\n")


def total_students():
    print(f"\nTotal number of students: {len(students)}\n")


def main():
    while True:
        print("=== Student Record Management System ===")
        print("1. Add Student")
        print("2. View All Students")
        print("3. Search Student by Roll Number")
        print("4. Update Student Information")
        print("5. Delete Student")
        print("6. Display Total Number of Students")
        print("7. Exit")

        choice = input("Enter your choice (1-7): ").strip()

        if choice == "1":
            add_student()
        elif choice == "2":
            view_students()
        elif choice == "3":
            search_student()
        elif choice == "4":
            update_student()
        elif choice == "5":
            delete_student()
        elif choice == "6":
            total_students()
        elif choice == "7":
            print("Exiting... Goodbye!")
            break
        else:
            print("\nInvalid choice. Please enter a number between 1-7.\n")


if __name__ == "__main__":
    main()