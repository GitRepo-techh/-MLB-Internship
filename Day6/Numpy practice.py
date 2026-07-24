import numpy as np


# NumPy

# 1. Implement programs to:
# 2. Create 1D and 2D arrays.
# 3. Perform arithmetic operations on arrays.
# 4. Find the maximum, minimum, mean, and sum of an array.
# 5. Reshape arrays into different dimensions.
# 6. Slice and index arrays.


# 1 & 2:

array1 = np.array([1, 2, 3, 4, 5])
array2 = np.array([[1, 2, 3], [4, 5, 6]])

print(array1)
print(array2)
print(array1.shape)
print(array2.shape)

# 3 & 4:


a = np.array([1, 2, 3, 4, 5])
print(a + 10)              # add 10 in every element in the array.
print(a.sum())             # sum the array.
print(a * a)               # multiply the array by itself.
print(a.max())             # to find the maximum value.
print(a.min())             # to find the minimum value.
print(a.mean())            # to fine the mean value.

# 5:

b = np.array([10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120])
# The product of both the numbers should not excede the bounds of the dimension of the array.
print(b.reshape(6,2))                  
print(b.reshape(-1,4))
print(b.reshape(2, -1))
print(b.reshape(4,3))




# 6:

array3 = np.array([[10, 20, 30], [40, 50, 60], [70, 80, 90]])
print(array3[0,1])
print(array3[1])
print(array3[ : , 2 ])    # : is actaully used to show what the other argument has passed, as it is used to view the elemnts in the array.
print(array3[0:2, 0:2])   # for a 2 by 2 matrix