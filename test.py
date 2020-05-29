'''
Created on Apr 29, 2020

@author: thaih
'''
import cv2
import numpy as np  


#load image and convert to hsv
img = cv2.imread("Rawmap_md.png")
cv2.imshow('Original', img)
# draw gray box around image to detect edge buildings
h,w = img.shape[:2]
cv2.rectangle(img,(0,0),(w-1,h-1), (50,50,50),1)

# convert image to HSV
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
cv2.imshow('HSV', img)


#low_gray = (0,0,0)
#high_gray = (95,11,241)

Lower_yellow = np.array([0,9,0])
Upper_yellow = np.array([50,20,255])
#Define dilation size
# d1 = 0
# d2 = 10
# d3 = 20
# t1 = cv2.MORPH_RECT
# kernel = cv2.getStructuringElement(t1, (2*d1 + 1, 2*d1+1), (d1, d1))
kernel = np.ones((2,2), dtype=np.uint8)

mask=cv2.inRange(hsv,Lower_yellow, Upper_yellow)
cv2.imshow("Get yellow", mask)

#kernel = np.ones((3,3), dtype=np.uint8)
mask = cv2.dilate(mask, kernel, iterations=1)

mask = cv2.erode(mask, kernel, iterations=1)
#image_GaussianBlur=cv2.GaussianBlur(mask,(9,9),10)
#image_MedianBlur = cv2.medianBlur(mask,9)
image_BilateralBlur=cv2.bilateralFilter(mask,9,100,75)
#cv2.imshow("Gauss",image_GaussianBlur)
#cv2.imshow("MedianBlur",image_MedianBlur)
cv2.imshow("BilateralBlur",image_BilateralBlur)

# mask = cv2.erode(mask, kernel, iterations=2)
# cv2.imshow("Get erode", mask)
# mask=cv2.morphologyEx(mask,cv2.MORPH_OPEN,kernel)
# 
# mask = cv2.dilate(mask, kernel, iterations=1)
# 
# res=cv2.bitwise_and(img,img,mask=mask)
# 
# 
# 
# edges = cv2.Canny(res,40,55,apertureSize = 3)
# cv2.imshow("Step-2: Get edges",edges)
# 
# cnts,heir=cv2.findContours(mask.copy(),cv2.RETR_EXTERNAL,cv2. CHAIN_APPROX_SIMPLE)[-2:]


#cv2.imshow("Result", res)
cv2.waitKey(0)
cv2.destroyAllWindows()