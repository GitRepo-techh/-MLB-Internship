import json

data = [ 
  {
        "Name": "Ali",
        "Roll Number": "2025-CE-2",
        "Course": "Computer Engineering",
        "Age": 17
    },
    {
        "Name": "Ahmed",
        "Roll Number": "2025-CE-1",
        "Course": "Computer Engineering",
        "Age": 18
    },  

]

with open(r"C:\VSCode\ML bench\Day4\data.json", "w") as f:
    json.dump(data, f, indent=4)  # indent=4 is used to format the JSON data with an indentation of 4 spaces for better readability.

with open(r"C:\VSCode\ML bench\Day4\data.json", "r") as f:
    data = json.load(f)
    print(data)

import json

def add_student(new_student):

    
    with open(r"C:\VSCode\ML bench\Day4\data.json", "r") as f:
        data = json.load(f)

    data.append(new_student) # this stores the new entry in it's memory

   
    with open(r"C:\VSCode\ML bench\Day4\data.json", "w") as f:  # as write mode rewrites everything so it takes the new list containing Maham and make a new json file.
        json.dump(data, f, indent=4)

new_data = {
    "Name": "Maham",
    "Roll Number": "2025-CE-3",
    "Course": "Computer Engineering",
    "Age": 19
}
add_student(new_data)