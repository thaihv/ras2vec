'''
Created on Apr 29, 2020

@author: thaih
'''
import cv2

# Read image as a map tile to cv
image = cv2.imread("Rawmap_1.png")
# draw gray box around image to detect edge buildings
h,w = image.shape[:2]
cv2.rectangle(image,(0,0),(w-1,h-1), (50,50,50),1)
cv2.imshow("Step-0: Select Map Tile",image) 

# Convert to gray
gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
cv2.imshow("Step-1: Make gray",gray)

# Apply Candy filter to get edges
edges = cv2.Canny(gray,40,55,apertureSize = 3)
cv2.imshow("Step-2: Get edges",edges)

# Revert colors to make edges is in black
edges = cv2.bitwise_not(edges)
cv2.imshow("Step-3: Revert Colors",edges)
cv2.waitKey(0)

# Blend with original image to get show
cv2.imwrite("edges.png", edges)
edgelines = cv2.imread("edges.png")
img = cv2.addWeighted(edgelines, 0.3, image, 0.7, 0)
cv2.imshow("Step-4: The result",img)
cv2.waitKey(0)