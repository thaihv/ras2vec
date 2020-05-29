import cv2
import numpy as np
import filters as fl

img = cv2.imread("X9.png")
cv2.imshow('Original', img)
# draw gray box around image to detect edge buildings
h,w = img.shape[:2]
cv2.rectangle(img,(0,0),(w-1,h-1), (50,50,50),1)
# 
# hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
# cv2.imshow('HSV', img)
# # define color ranges
# low_yellow = (0,9,0)
# high_yellow = (15,255,255)
# low_gray = (0,0,0)
# high_gray = (95,11,241)
# # create masks
# yellow_mask = cv2.inRange(hsv, low_yellow, high_yellow )
# cv2.imshow("SELECT WALL YELLOW", yellow_mask)
# 
# gray_mask = cv2.inRange(hsv, low_gray, high_gray)
# cv2.imshow("SELECT WALL GRAY", gray_mask)
# # combine masks
# combined_mask = cv2.bitwise_or(yellow_mask, gray_mask)
# #wall = cv2.bitwise_and(img,img, mask = combined_mask)
# cv2.imshow("SELECT WALL", combined_mask)

#fl.strokeEdges(img, img, 2,5)

kernel = np.array([[-1, -1, -1],
					[-1, 9, -1],
					[-1, -1, -1]])

# myfilter = fl.VConvolutionFilter(kernel)
# myfilter.apply(img, img)

fl.SharpenFilter().apply(img, img)
cv2.imshow("Sharpen", img)
cv2.imwrite('XB.png', img)
#fl.FindEdgesFilter().apply(img, img)
#fl.BlurFilter().apply(img, img)
# fl.EmbossFilter().apply(img, img)
# cv2.imshow("Emboss", img)

# img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV);
# cv2.imshow("Candy", cv2.Canny(img, 640, 640))
cv2.waitKey()
cv2.destroyAllWindows()