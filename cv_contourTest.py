import cv2
import numpy as np

img = cv2.imread("Rawmap_1.png")
img2 = img.copy()
#cv2.imshow('Original', img)
# draw gray box around image to detect edge buildings
h,w = img.shape[:2]
cv2.rectangle(img,(0,0),(w-1,h-1), (50,50,50),1)
 
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
#cv2.imshow('HSV', img)
# define color ranges
low_yellow = (0,9,0)
high_yellow = (15,255,255)
low_gray = (0,0,0)
high_gray = (95,11,241)
# create masks
yellow_mask = cv2.inRange(hsv, low_yellow, high_yellow )
#cv2.imshow("SELECT WALL YELLOW", yellow_mask)
 
gray_mask = cv2.inRange(hsv, low_gray, high_gray)
#cv2.imshow("SELECT WALL GRAY", gray_mask)
# combine masks
combined_mask = cv2.bitwise_or(yellow_mask, gray_mask)
#wall = cv2.bitwise_and(img,img, mask = combined_mask)
cv2.imshow("SELECT WALL", combined_mask)
# kernel = np.ones((3,3), dtype=np.uint8)
# combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_DILATE,kernel)

kernel = np.ones((3,3),np.uint8)
# kernel = np.array([[-1, -1, -1],
# 					[-1, 9, -1],
# 					[-1, -1, -1]])
combined_mask = cv2.morphologyEx(combined_mask,cv2.MORPH_OPEN,kernel, iterations = 1)

#combined_mask = cv2.dilate(combined_mask,kernel,iterations=3)
#combined_mask = cv2.connectedComponents(combined_mask)

cv2.imshow("DILATION THEN EROSION", combined_mask)

contours, hier = cv2.findContours(combined_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

for x in range(len(contours)):
		# if a contour has not contours inside of it, draw the shape filled
		c = hier[0][x][2]
		if c == -1:
			#cv2.drawContours(img,[contours[x]],0,(0,0,255),-1) 
			cnt = [contours[x]][0]
			if cv2.contourArea(cnt) > 80:
				cnt = [contours[x]][0]
				epsilon = 0.0001*cv2.arcLength(cnt, True)
				approx = cv2.approxPolyDP(cnt, epsilon, True)
				cv2.drawContours(img, [approx], -1, (0,0,255), -1)
				cv2.imshow('Buildings in RED', img)
				#cv2.waitKey(0)
for cnt in contours:
# 	hull = cv2.convexHull(cnt)
# 	hullimg = img.copy()
# 	cv2.drawContours(img,[hull],0,(147,0,255),2)
# 	cv2.imshow("HULL",img)
	cv2.drawContours(img,[cnt],0,(0,255,0),1)
		
	
#cv2.drawContours(img, contours, -1, (255, 0, 0), 1)
cv2.imshow("contours", img)

edges = cv2.Canny(hsv,640,640)
cv2.imshow("Candy", edges)
minLineLength = 20
maxLineGap = 10
lines = cv2.HoughLinesP(edges,1,np.pi/180,500,minLineLength, maxLineGap)
for x1,y1,x2,y2 in lines[0]:
	cv2.line(img2,(x1,y1),(x2,y2),(0,0,255),2)
cv2.imshow("Hough Lines", img2)

cv2.waitKey()
cv2.destroyAllWindows()