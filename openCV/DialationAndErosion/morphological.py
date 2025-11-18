import cv2
import numpy as np

img = cv2.imread("smarties.png",0)  
_,mask=cv2.threshold(img,220,255,cv2.THRESH_BINARY_INV)

kernel = np.ones((5,5),np.uint8)
dilation = cv2.dilate(mask,kernel,iterations=2) #Dilates the mask image by extend the pixels of the object.
erosion = cv2.erode(mask,kernel,iterations=4) #Erodes the mask image by shrink the pixels of the object.
opening = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel,iterations=1) #Performs an opening operation on the mask image.
closing = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel,iterations=1) #Performs a closing operation on the mask image.

cv2.imshow("Image",img)
cv2.imshow("Mask",mask)
cv2.imshow("Dilation",dilation)
cv2.imshow("Erosion",erosion)
cv2.imshow("Opening",opening)
cv2.imshow("Closing",closing)
cv2.waitKey(0)
cv2.destroyAllWindows()