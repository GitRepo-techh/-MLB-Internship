# OOP

# Create a Student class.
# Create an Employee class.
# Create a Car class with different attributes and methods.
# Create multiple objects from the same class.


# 1.
class Student:
    def __init__(self,name,age):
        self.name = name 
        self.age = age
    def display(self):
        print(f"Name: {self.name}, Age: {self.age}")
call = Student("John", 20)
call.display()

# 2:
class Employee:
    def __init__(self,name,salary, working_hours):
        self.name = name
        self.salary = salary
        self.working_hours = working_hours
    def show(self):
        print(f"Your salary is {self.salary}")
    def show_working_hours(self):
        print(f"Your working hours per day are {self.working_hours}")
    def bonus(self, identify):
        if self.working_hours >= 12:
            self.salary = identify + self.salary
call = Employee("Howrd", 34000 , 13)
call.show()
call.show_working_hours()
call.bonus(1200)
call.show()
# 3:
class Car():
    def __init__(self, model, brand):
        self.model = model
        self.brand = brand
    def show_model(self):
        print(f"You car model is {self.model}")
    def show_brand(self):
        print(f"Your car brand is {self.brand}")
call = Car("2020", "Toyota")
call.show_model()
call.show_brand()

# 4:
class Student:
    def __init__(self,name,age):
        self.name = name 
        self.age = age
    def display(self):
        print(f"Name: {self.name}, Age: {self.age}")
call1 = Student("John", 20)
call2 = Student("Alice", 22)
print(call1.name)
print(call2.age)







# Inheritance

# 1. Create a Person class.
# 2. Create Student and Teacher classes inheriting from Person.
# 3. Override methods where appropriate.

# 1 & 2 & 3:
class Person:
    def __init__(self,name,age):
        self.name = name
        self.age = age
    def introduce(self):
        return f"Hi, I'm {self.name} and I'm {self.age} years old."
 
    def role(self):
        return "Person"

class Student(Person):
    def __init__(self, name ,age , roll_no, department):
        super().__init__(name, age)
        self.roll_no = roll_no
        self.department = department
    def show_roll_no(self):
        print(f"Your roll_no  is {self.roll_no}")
    def role(self):
        return "Student"
class Teacher(Person):
    def __init__ (self, name , age, experience, department):
        super().__init__(name, age)
        self.experience =  experience
        self.daepartment = department
    def show_expereince(self):
        print(f"Your experience is {self.experience}")  
    def role(self):
        return "Teacher"


s = Student("Ayesha", 20, "2025-CE-050", "Electrical Engineering")
print(s.introduce())     # inherited from Person
print(s.role())          # overridden in Student
s.show_roll_no()         # Student-only method

t = Teacher("Dr. Ahmed", 45, 10, "Computer Science")
print(t.introduce())     # inherited from Person
print(t.role())          # overridden in Teacher
t.show_expereince() 

    