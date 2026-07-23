import json
import os

class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def introduce(self):
        return f"Hi, I'm {self.name} and I'm {self.age} years old."

    def role(self):
        return "Person"


class Student(Person):
    def __init__(self, name, age, roll_no):
        super().__init__(name, age)
        self.roll_no = roll_no
        self.borrowed_books = []

    def role(self):
        return "Student"


class Teacher(Person):
    def __init__(self, name, age, department):
        super().__init__(name, age)
        self.department = department
        self.borrowed_books = []

    def role(self):
        return "Teacher"


class Book:
    def __init__(self, title, author, isbn, total_copies, available_copies=None):
        self.title = title
        self.author = author
        self.isbn = isbn
        self.total_copies = total_copies
        if available_copies is None:
            self.available_copies = total_copies
        else:
            self.available_copies = available_copies

    def show(self):
        print(f"[{self.isbn}] {self.title} by {self.author} ({self.available_copies}/{self.total_copies} available)")


class Library:
    def __init__(self):
        self.books = {}
        self.members = {}
        self.load_data()

    def load_data(self):
        if not os.path.exists("library_data.json"):
            return
        try:
            with open("library_data.json", "r") as f:
                data = json.load(f)

            for b in data["books"]:
                book = Book(b["title"], b["author"], b["isbn"], b["total_copies"], b["available_copies"])
                self.books[book.isbn] = book

            for m in data["members"]:
                if m["type"] == "Student":
                    member = Student(m["name"], m["age"], m["roll_no"])
                else:
                    member = Teacher(m["name"], m["age"], m["department"])
                member.borrowed_books = m["borrowed_books"]
                self.members[member.name] = member

        except (json.JSONDecodeError, KeyError):
            print("Could not read saved data, starting fresh.")

    def save_data(self):
        books_list = []
        for book in self.books.values():
            books_list.append({
                "title": book.title,
                "author": book.author,
                "isbn": book.isbn,
                "total_copies": book.total_copies,
                "available_copies": book.available_copies
            })

        members_list = []
        for member in self.members.values():
            if isinstance(member, Student):
                members_list.append({
                    "type": "Student",
                    "name": member.name,
                    "age": member.age,
                    "roll_no": member.roll_no,
                    "borrowed_books": member.borrowed_books
                })
            else:
                members_list.append({
                    "type": "Teacher",
                    "name": member.name,
                    "age": member.age,
                    "department": member.department,
                    "borrowed_books": member.borrowed_books
                })

        data = {"books": books_list, "members": members_list}
        with open("library_data.json", "w") as f:
            json.dump(data, f, indent=4)

    def add_book(self, title, author, isbn, total_copies):
        if isbn in self.books:
            print("This book already exists.")
            return
        book = Book(title, author, isbn, total_copies)
        self.books[isbn] = book
        self.save_data()
        print("Book added successfully.")

    def view_books(self):
        if not self.books:
            print("No books available.")
            return
        for book in self.books.values():
            book.show()

    def search_book(self, keyword):
        found = False
        for book in self.books.values():
            if keyword.lower() in book.title.lower() or keyword.lower() in book.author.lower():
                book.show()
                found = True
        if not found:
            print("No matching books found.")

    def register_member(self, member):
        if member.name in self.members:
            print("Member already registered.")
            return
        self.members[member.name] = member
        self.save_data()
        print(f"{member.role()} registered: {member.introduce()}")

    def view_members(self):
        if not self.members:
            print("No members registered.")
            return
        for member in self.members.values():
            print(f"{member.role()}: {member.name} - Borrowed: {member.borrowed_books}")

    def borrow_book(self, member_name, isbn):
        if member_name not in self.members:
            print("Member not found.")
            return
        if isbn not in self.books:
            print("Book not found.")
            return

        book = self.books[isbn]
        member = self.members[member_name]

        if book.available_copies <= 0:
            print("No copies available right now.")
            return

        book.available_copies -= 1
        member.borrowed_books.append(isbn)
        self.save_data()
        print(f"{member.name} borrowed '{book.title}'.")

    def return_book(self, member_name, isbn):
        if member_name not in self.members:
            print("Member not found.")
            return
        if isbn not in self.books:
            print("Book not found.")
            return

        book = self.books[isbn]
        member = self.members[member_name]

        if isbn not in member.borrowed_books:
            print(f"{member.name} did not borrow this book.")
            return

        book.available_copies += 1
        member.borrowed_books.remove(isbn)
        self.save_data()
        print(f"{member.name} returned '{book.title}'.")


def main():
    library = Library()

    while True:
        print("\n1. Add book")
        print("2. View books")
        print("3. Search book")
        print("4. Register member")
        print("5. View members")
        print("6. Borrow book")
        print("7. Return book")
        print("8. Exit")

        choice = input("Enter choice: ")

        try:
            if choice == "1":
                title = input("Title: ")
                author = input("Author: ")
                isbn = input("ISBN: ")
                total_copies = int(input("Total copies: "))
                library.add_book(title, author, isbn, total_copies)

            elif choice == "2":
                library.view_books()

            elif choice == "3":
                keyword = input("Search keyword: ")
                library.search_book(keyword)

            elif choice == "4":
                member_type = input("Register as (1) Student or (2) Teacher: ")
                name = input("Name: ")
                age = int(input("Age: "))

                if member_type == "1":
                    roll_no = input("Roll no: ")
                    library.register_member(Student(name, age, roll_no))
                elif member_type == "2":
                    department = input("Department: ")
                    library.register_member(Teacher(name, age, department))
                else:
                    print("Invalid choice.")

            elif choice == "5":
                library.view_members()

            elif choice == "6":
                member_name = input("Member name: ")
                isbn = input("Book ISBN: ")
                library.borrow_book(member_name, isbn)

            elif choice == "7":
                member_name = input("Member name: ")
                isbn = input("Book ISBN: ")
                library.return_book(member_name, isbn)

            elif choice == "8":
                print("Goodbye!")
                break

            else:
                print("Invalid choice, try again.")

        except ValueError:
            print("Invalid input, please enter correct values.")


if __name__ == "__main__":
    main()