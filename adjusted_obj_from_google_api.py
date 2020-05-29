import cv2
import numpy as np  
from skimage import io
from skimage import color
import utils


img = cv2.imread("mdd_red.png")
#img1 = cv2.imread("black.png")
cv2.imshow('Original', img)

# img = cv2.subtract(img,img1)
# cv2.imshow('Subtracted',img)

# draw gray box around image to detect edge buildings
h,w = img.shape[:2]
cv2.rectangle(img,(0,0),(w-1,h-1), (50,50,50),1)

hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
cv2.imshow('HSV', img)

low = (0,11,0)
high = (179,255,255)

# create masks
mask = cv2.inRange(hsv, low, high)
cv2.imshow("RANGES", mask)

# kernel = np.ones((3,3),np.uint8)
# walls = utils.erosionthendilation(mask, kernel)
#    
# cv2.imshow("REMOVE NOISE", walls)
 
# findcontours
contours, hier = cv2.findContours(mask,cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

for x in range(len(contours)):
	print()
	# if a contour has not contours inside of it, draw the shape filled
	c = hier[0][x][2]
	if c == -1:
		cv2.drawContours(img,[contours[x]],0,(0,0,255),-1) 
		cv2.imshow('Buildings in RED', mask)
		cv2.waitKey(0)
 
# draw the outline of all contours
for cnt in contours:
		cv2.drawContours(mask,[cnt],0,(0,255,0),1)

# display result
cv2.imshow("Result", mask)
cv2.waitKey(0)
cv2.destroyAllWindows() 