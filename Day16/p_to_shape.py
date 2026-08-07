import cv2
import numpy as np 




image = cv2.imread("pictures/lamb.png", 1 )
width = image.shape[1]
height = image.shape[0]




reactangle = cv2.rectangle(image, (56,56), (200,132), (234,65,136), 2)
line = cv2.line(image, (0,0), (width, height), (255,32,0), 2)
circle = cv2.circle(image, (100,100), 120, (10,25,100), 2)
polygon = cv2.polylines(image, [np.array([[10,5], [20,30], [70,20], [50,10]], np.int32)], True, (0,255,0), 2)
text = cv2.putText(image, "Hello World", (10,100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)

cv2.imshow("Image", image)

cv2.waitKey(0)
cv2.destroyAllWindows()