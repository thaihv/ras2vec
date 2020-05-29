import cv2
import numpy as np
import sys

img = cv2.imread("Rawmap_1.png")

h,w = img.shape[:2]
cv2.rectangle(img,(0,0),(w-1,h-1), (50,50,50),1)
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
cv2.imshow('HSV', img)

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
combined_mask = cv2.morphologyEx(combined_mask,cv2.MORPH_OPEN,kernel, iterations = 1)


combined_mask = np.float32(combined_mask)
dst = cv2.cornerHarris(combined_mask, 2, 23, 0.04)
print(dst)
img[dst > 0.01 * dst.max()] = [0, 0, 255]

# sift = cv2.xfeatures2d.SIFT_create()
# keypoints, descriptor = sift.detectAndCompute(combined_mask,None)
# img = cv2.drawKeypoints(image=img, outImage=img, keypoints = keypoints, flags = cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS, color = (51, 163, 236))

while (True):
	cv2.imshow('corners', img)
	#if cv2.waitKey(int(1000 / 12)) & 0xff == ord("q"):
	if cv2.waitKey():
		break
cv2.destroyAllWindows()
