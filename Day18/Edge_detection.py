import cv2
import numpy as np


# Coding Practice
# Implement the following programs:
# 1: Convert an image to grayscale.
# 2: Apply Gaussian Blur before edge detection.
# Detect edges using:
# a. Sobel
# b. Laplacian
# c. Canny
# d. Compare the output of all three edge detection methods.
# e. Apply each morphological operation separately.
# f. Compare the images before and after applying morphological operations.


# 1 & 2.
# a.
# Sobel:


image1 = cv2.imread("Input images/image4.jpg", 0)
blur = cv2.GaussianBlur(image1, (5,5), sigmaX = 0)
resize = cv2.resize(blur, (300,300))

Sobel_x = cv2.Sobel(blur, cv2.CV_64F, 1, 0, ksize = 3)
Sobel_y = cv2.Sobel(blur, cv2.CV_64F, 0, 1, ksize = 3)
# we use CV_64F here beacuse sobel gives us values ranging in -ve too and unit8 doesn't have this value. 

# We later convert it into unit8 because that is essential for getting a 8-bit image.
convert_x = cv2.convertScaleAbs(Sobel_x)
convert_y = cv2.convertScaleAbs(Sobel_y)

# We can combine them to see the result as a whole.
sobel = cv2.addWeighted(convert_x, 0.5, convert_y, 0.5, 0)  # 0.5 here helps even the combination so that both x and y get 50% of the image.
# addweighted = image1 * α  + image2 * β  + γ




resize_sobel_x = cv2.resize(convert_x, (500, 500))
resize_sobel_y = cv2.resize(convert_y, (500, 500))
resize_sobel = cv2.resize(sobel, (400, 400))


cv2.imshow("Original_Image", image1)
cv2.imshow("Blur_Image", resize)
cv2.imshow("Sobel_x", resize_sobel_x)
cv2.imshow("Sobel_y", resize_sobel_y)
cv2.imshow("Sobel_Image", resize_sobel)

cv2.waitKey(0)
cv2.destroyAllWindows()

# b.
# Laplace:


image2 = cv2.imread("Input images/image4.jpg", 0)
blur = cv2.GaussianBlur(image2, (3,3), sigmaX = 0)



laplace = cv2.Laplacian(blur, cv2.CV_64F)

combine = cv2.convertScaleAbs(laplace) # converts 64 bit into 8


image_ = cv2.resize(image2, (500,500))
laplace_ = cv2.resize(combine, (400,400))

cv2.imshow("Original_image", image_)
cv2.imshow("Laplace image", laplace_)

cv2.waitKey(0)
cv2.destroyAllWindows()


# c.
# Canny:


image3 = cv2.imread("Input images/image4.jpg", 0)
blur = cv2.GaussianBlur(image3, (7,7), 0)

canny = cv2.Canny(blur, 10, 100) # These are the lower and upper thresholds, which means that the images pixels below this threshold gets ignored while the pixels above this throeshold are sure to be edges while pixels between them if joined by a pixel of higher threshold are termed as edges otherwise discarded.


image__= cv2.resize(image3, (600,600))
canny1 = cv2.resize(canny, (400,400))

cv2.imshow("Image", image__)
cv2.imshow("Canny", canny1)


comparison = np.hstack((resize_sobel, laplace_, canny1))

cv2.imshow("Comparison: Sobel | Laplacian | Canny", comparison)
cv2.waitKey(0)
cv2.destroyAllWindows()

# d.
kernel = np.ones((7,7),np.uint8)

# Errosion:
errosion = cv2.erode(image1, kernel, iterations = 2) # This function removes small white noise, makes objects thinner
r_ero = cv2.resize(errosion, (300,300))

# Dilution:
dilate = cv2.dilate(image2, kernel, iterations = 2) # This function removes small black noise or sort of fills teh white the samll white spaces. You can also say it grows the oject.
r_dil = cv2.resize(dilate, (300,300))

# Open-Head:
open_head = cv2.morphologyEx(image3, cv2.MORPH_OPEN, kernel) # This is errosion - dillution. It removes small spaces in the kernel area.
r_open = cv2.resize(open_head, (300,300))

# Close-Head:
close = cv2.morphologyEx(image__, cv2.MORPH_CLOSE, kernel) # This is dilution - errosion. It fills small spaces in the kernel area.
r_close = cv2.resize(close, (300,300))

# f.

stack = np.hstack((r_ero,r_dil,r_open,r_close))
cv2.imshow("Compariosn: Erroded | Dilluted | Open | Close", stack)


cv2.waitKey(0)
cv2.destroyAllWindows()
