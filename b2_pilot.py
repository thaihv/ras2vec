import cv2
import numpy as np  

#load image and convert to hsv
img = cv2.imread("Rawmap_1.png")
cv2.imshow('Original', img)
# draw gray box around image to detect edge buildings
h,w = img.shape[:2]
cv2.rectangle(img,(0,0),(w-1,h-1), (50,50,50),1)

# convert image to HSV
grayscale = cv2.imread('Rawmap_1.png', cv2.IMREAD_GRAYSCALE)
cv2.imshow('IMREAD_GRAYSCALE', grayscale)


threshold = cv2.adaptiveThreshold(grayscale,255,cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY,11,2)
cv2.imshow("SELECT WALL", threshold)

kernel = np.ones((3,3), dtype=np.uint8)
combined_mask = cv2.morphologyEx(threshold, cv2.MORPH_DILATE,kernel)

cv2.imshow("DILATE", combined_mask)

# findcontours
contours, hier = cv2.findContours(combined_mask,cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

# find and draw buildings
for x in range(len(contours)):
		# if a contour has not contours inside of it, draw the shape filled
		c = hier[0][x][2]
		if c == -1:
				cv2.drawContours(img,[contours[x]],0,(0,0,255),-1)

cv2.imshow('Buildings in RED', img)

# draw the outline of all contours
for cnt in contours:
		cv2.drawContours(img,[cnt],0,(0,255,0),2)

# display result
cv2.imshow("Result", img)
cv2.waitKey(0)
cv2.destroyAllWindows() 