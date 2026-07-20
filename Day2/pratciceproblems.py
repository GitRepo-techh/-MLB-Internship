# For Lists:
# 1. Find the largest number in a list.
# 2. Find the second largest number.
# 3. Remove duplicate values from a list.
# 4. Reverse a list without using built-in reverse().
# 5. Find common elements between two lists.


# 1 and 2:
lst = [0, 12, 34, 4, 9]
maximum = max(lst)
print(maximum)
maximum_ = max(lst)
lst.remove(maximum_)
maximum_new_list = max(lst)
print(maximum_new_list)
lst.append(maximum_)
print(lst)


# 3:
numbers = [0, 0, 2, 3, 4, 4, 5, 7, 10]
numbers = set(numbers)
new_list = list(numbers)
print(new_list)


# 4:
normal_list = [12, "Apples", 64, 0]
reversed_list = normal_list[::-1]
print(reversed_list)


# 5:
list1 = [ 1, 2, 3, 4, 5, 7, 9]
list2 = [ 1, 0, 3, 8, 12, 7, 43]
new_list = []
for items in list1:
    for item in list2:
        if item == items:
          new_list.append(item)
print(new_list)          # or you could have just transformed the list into a set taken an intersection and than cinverted it back into a list.



# Tuples:
# 1. Count occurrences of an element.
# 2.Convert a tuple into a list and vice versa.

# 1:
tuple1 = (1, 2, 4, 6, 9, 10, 45)
even_numbers = sum(1 for item in tuple1 if item % 2 == 0)
print(even_numbers)

# 2:
tuple1 = (1, 2, 4, 6, 9, 10, 45)
list1 = list(tuple1)
tuple1 = tuple(list1)
print(list1)
print(tuple1)






# Sets:
# 1. Find unique values from a list.
# 2. Perform union and intersection operations.


# 1:
numbers = [0, 0, 2, 3, 4, 4, 5, 7, 10]
numbers = set(numbers)
print(numbers)   

# 2:
set1 = {1, 3, 5, 2, 8, 10}
set2 = {2, 4, 6, 1, 9, 7}
print(set1 | set2) # For Union
print(set1 & set2) # For Intersection







# Dictionaries:
# 1. Create a student record dictionary.
# 2. Calculate average marks of students.
# 3. Count frequency of words in a sentence.

# 1 & 2:
student_record = {
    "Farhan": {"Age": 18, "Gender": "Male", "Marks": [85, 90, 78]},
    "Asad": {"Age": 19, "Gender": "Male", "Marks": [70, 65, 80]},
    "Ayesha": {"Age": 20, "Gender": "Female", "Marks": [95, 88, 92]}
}


for name, info in student_record.items():
    marks = info["Marks"]
    average = sum(marks) / len(marks)
    print(f"{name}'s average marks: {average:.2f}")



# 3:
sentence = "the quick brown fox jumps over the lazy dog the fox runs"
words = sentence.split()

word_count = {}

for word in words:
    if word in word_count:
        word_count[word] += 1
    else:
        word_count[word] = 1

print(word_count)
