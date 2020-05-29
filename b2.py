import cv2
import numpy as np  

#load image and convert to hsv
img = cv2.imread("Rawmap_1.png")
cv2.imshow('Original', img)
# draw gray box around image to detect edge buildings
h,w = img.shape[:2]
cv2.rectangle(img,(0,0),(w-1,h-1), (50,50,50),1)

# convert image to HSV
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
cv2.imshow('HSV', img)

#low_yellow = (0,28,0)
#high_yellow = (27,255,255)

#low_gray = (0,0,0)
#high_gray = (179,255,233)

# define color ranges
low_yellow = (0,9,0)
high_yellow = (15,255,255)

low_gray = (0,0,0)
high_gray = (95,11,241)

# create masks
yellow_mask = cv2.inRange(hsv, low_yellow, high_yellow )
cv2.imshow("SELECT WALL YELLOW", yellow_mask)

gray_mask = cv2.inRange(hsv, low_gray, high_gray)
cv2.imshow("SELECT WALL GRAY", gray_mask)

# combine masks
combined_mask = cv2.bitwise_or(yellow_mask, gray_mask)
#wall = cv2.bitwise_and(img,img, mask = combined_mask)
cv2.imshow("SELECT WALL", combined_mask)

kernel = np.ones((3,3), dtype=np.uint8)
combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_DILATE,kernel)

cv2.imshow("DILATE", combined_mask)

# find contours
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
		cv2.drawContours(img,[cnt],0,(0,255,0),1)

# display result
cv2.imshow("Result", img)
cv2.waitKey(0)
cv2.destroyAllWindows() 