import cv2
import numpy as np

# Coding Practice:

# Implement programs to:

# 1. Translate an image horizontally and vertically.
# 2. Rotate an image by different angles.
# 3. Scale an image up and down.
# 4. Apply an affine transformation.
# 5. Apply a perspective transformation to straighten a tilted document.
# 6. Increase and decrease image brightness.
# 7. Adjust image contrast.
# 8. Apply Gaussian Blur, Median Blur, and Bilateral Filter.
# 9. Sharpen the image using an image sharpening filter.


# 1:
def translate_image():



    image = cv2.imread("Input images/tree.png", 1)
    image2 = cv2.imread("Input images/image1.jpg", 1)
    # Shift images by this value:
    tx = 129
    ty = 100
    matrix = np.float32([[1, 0, tx], [0, 1, ty]])  # opencv needs a numpy array of float32 type.

    shape = image.shape[:2]  # this will gives us teh shape and we are only getting the width and height of the image not the channels by slicing it.
    shape1 = image2.shape[:2]


    warp = cv2.warpAffine(image, matrix, shape)
    warp1 = cv2.warpAffine(image2, matrix, shape1)


    cv2.imshow("Original_Image", image)
    cv2.imshow("Warped_Image", warp)

    cv2.imshow("Original_Image2", image2)
    cv2.imshow("Warped_Image2", warp1)


    cv2.imwrite("Output images/warped_image.png", warp)
    cv2.imwrite("Output images/warped_image2.png", warp1)

    cv2.waitKey(0)
    cv2.destroyAllWindows()


# 2:
def rotation():
    image = cv2.imread("Input images/lamb.png", 1)

    width, height = image.shape[:2]

    center = (width // 2, height // 2)


    rotate = cv2.getRotationMatrix2D(center, 45, 1.0)  # 45 is the angle and 1.0 is the scale factor which tells us how much we want to scale the image. 1.0 means no scaling, 0.5 means half the size, 2.0 means double the size adn so on.

    # we use getWarpAffine to apply all the functions performed to the image by functions like getRotationMatrix2D, getAffineTransform, getPerspectiveTransform etc.
    warp = cv2.warpAffine(image, rotate, (width, height))  # this will apply the rotation to the image and return the rotated image.

    cv2.imshow("Original_Image", image)
    cv2.imshow("Warped_Image", warp)

    cv2.imwrite("Output images/warped_image3.png", warp)

    cv2.waitKey(0)
    cv2.destroyAllWindows()

# 3:
def scaling():
    image = cv2.imread("Input images/image2.jpg", 1)

    scaled_up = cv2.resize(image, None, fx = 0.2, fy = 0.2, interpolation = cv2.INTER_CUBIC) # we use intr_cubic here beacuse it is a better interpolation method for scaling up images. It uses the values of the 16 nearest pixels to calculate the new pixel value. It is slower than other methods but gives better results.
    scaled_down = cv2.resize(image, None, fx = 0.5, fy = 0.5, interpolation = cv2.INTER_AREA) 
    # The None here represents the output size of the image. We can also specify the output of the image here.

    cv2.imshow("Original_Image", image)
    cv2.imshow("Scaled_Up_Image", scaled_up)
    cv2.imshow("Scaled_Down_Image", scaled_down)

    cv2.waitKey(0)
    cv2.destroyAllWindows()

# 4:
def affine_transformation():

    image = cv2.imread("Input images/tilted_document.jpg", 1)
    col, rows = image.shape[:2]

    pts1 = np.float32([[19,92], [76, 573], [372, 48]])    # these are the points that we want to transform. We can either automate it to slect it automatically by using corner detection and canny or we can manually select them.
    pts2 = np.float32([[0, 0], [0, rows], [col, 0]])

    matrix = cv2.getAffineTransform(pts1, pts2)
    affine = cv2.warpAffine(image, matrix, (col, rows))


    cv2.imshow("Original Image", image)
    cv2.imshow('Affine', affine)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# 5:

def perspective_transformation():

    image = cv2.imread("Input images/tilted_document.jpg", 1)
    col, rows = image.shape[:2]

    pts1 = np.float32([[19,92], [76, 573], [372, 48], [432, 554]])    # these are the points that we want to transform. We can either automate it to slect it automatically by using corner detection and canny or we can manually select them.
    pts2 = np.float32([[0, 0], [0, rows], [col, 0], [col, rows]]) # the first list represents the Top left corner, the second list represents the Bottom left corner, the third list represents the Top right corner and the fourth list represents the Bottom right corner of the image.

    matrix = cv2.getPerspectiveTransform(pts1, pts2)
    affine = cv2.warpPerspective(image, matrix, (col, rows))


    cv2.imshow("Original Image", image)
    cv2.imshow('Perspective', affine)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# 6:
def brightness():

    img = cv2.imread('Input images/cat.jpg', 1)

    brighter = cv2.convertScaleAbs(img, alpha=1.0, beta=50)   # +50 brightness
    darker   = cv2.convertScaleAbs(img, alpha=1.0, beta=-50)  # -50 brightness

    cv2.imshow('Brighter', brighter)
    cv2.imshow('Darker', darker)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# 7:
def contrast():

    image = cv2.imread("Input images/tree.png", 1)

    high_contrast = cv2.convertScaleAbs(image, alpha=1.5, beta=0)  # >1 = more contrast
    low_contrast  = cv2.convertScaleAbs(image, alpha=0.5, beta=0)  # <1 = less contrast

    cv2.imshow('Combined', np.hstack((high_contrast, low_contrast)))
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# 8:

def blurring():
    
    image = cv2.imread("Input images/goat.jpg", 1)

    gaussian = cv2.GaussianBlur(image, (13, 13), sigmaX = 8, sigmaY = 5) # 13, 13 represents the kernel size. teh sigma x and y determine how teh blur will spread out.
    median   = cv2.medianBlur(image, 23) # here 23 is the kernel size.
    bilateral = cv2.bilateralFilter(image, d=9, sigmaColor=198, sigmaSpace=198)  # d is the diameter of the pixel neighborhood, sigmaColor is the filter sigma in the color space, and sigmaSpace is the filter sigma in the coordinate space. The larger these values, the more the filter will smooth out the image while preserving edges. 

    cv2.imshow('Gaussian Blur', gaussian)
    cv2.imshow('Median Blur', median)
    cv2.imshow('Bilateral Filter', bilateral)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# 9:
def sharpening():
    image = cv2.imread("Input images/tree.png", 1)
    kernel = np.array([[ 0, -1,  0],
                        [-1, 5, -1],
                        [ 0, -1, 0]])

    sharpened = cv2.filter2D(image, -1, kernel)

    cv2.imshow('Sharpened', sharpened)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


functions = ["translate_image", "rotation", "scaling", "affine_transformation", "perspective_transformation", "brightness", "contrast", "blurring", "sharpening"]
print(f"Which function do you want to run? {functions}")
user = input("Enter you choice: (1-9)").strip()
for func in functions:
    if user == "1":
        translate_image()
        break
    if user == "2":
        rotation()  
        break
    if user == "3":
        scaling()
        break
    if user == "4":
        affine_transformation()
        break
    if user == "5":
        perspective_transformation()
        break
    if user == "6":
        brightness()
        break
    if user == "7":
        contrast()
        break
    if user == "8":
        blurring()
        break
    if user == "9":
        sharpening()
        break
