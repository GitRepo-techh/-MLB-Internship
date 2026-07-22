# File Handling

# 1.Create a text file and write data into it.
# 2.Read and display file contents.
# 3.Append new data to an existing file.
# 4.Count the number of lines in a file.


# 1. Create a text file and write data into it
def one():
    file = open(r"C:\VSCode\ML bench\Day4\text.txt", "w") # tells Python to treat backslashes as literal characters instead of escape characters.
    file.write("HI world!")

    file.close()

# 2.
def read_file():
    file = open(r"C:\VSCode\ML bench\Day4\text.txt", "r")
    readd = file.read()
    print(readd)
    file.close()

# 3.
def append_to_file():
    file = open(r"C:\VSCode\ML bench\Day4\text.txt", "a")
    file.write("So, How you doin' \n")
    file.close()

# 4. 
def line_count():
    with open(r"C:\VSCode\ML bench\Day4\text.txt", "r") as f:
        line = f.readlines()
        print(len(line))

line_count()
