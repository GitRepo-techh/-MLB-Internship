import cv2 




image = cv2.imread("pictures/lamb.png", 1 ) # 1 means we want to read the image in color.
image2 = cv2.imread("pictures/car.png", 1 )
image3 = cv2.imread("pictures/avatar.png", 0 ) # We use 0 for grayscale here. 


# What are the channels and shape of the image:
print(f"The shape of the lamb image is {image.shape}")  # .shape tells the width height and teh nu. of channels in the image.
print(f"The size of the lamb image is {image.size}") # .size basically gives the total number of pixels in the image.

# Resize and Roatate the image:
image = cv2.resize(image, (300,200)) 
image = cv2.rotate(image, cv2.ROTATE_180)
image2 = cv2.resize(image2, (0,0), fx = 0.5, fy = 0.5)
image2 = cv2.rotate(image2, cv2.ROTATE_90_CLOCKWISE)



# Crop the image:
image2_cropped = image2 [0 : 234, 2: 231] # Cropping the image to a specific region of interest.


# Show all the images:
cv2.imshow("Image", image) 
cv2.imshow("Image2", image2)
cv2.imshow("Image2 Cropped", image2_cropped)
cv2.imshow("Image3", image3)


cv2.waitKey(0) # Waits for a key press to close the image window. 0 beacuse it allows us to wait indefinately until a key is pressed.
cv2.destroyAllWindows() # Closes all the image windows opened by OpenCV.