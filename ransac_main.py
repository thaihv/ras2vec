'''
Created on Apr 28, 2020

@author: thaih
'''
import numpy as np
import cv2
from Ransac import *
from Affine import *
from Align import *

img_source = cv2.imread("f.png")
img_target = cv2.imread("Raw_18.png")
keypoint_source, descriptor_source = extract_SIFT(img_source)
keypoint_target, descriptor_target = extract_SIFT(img_target)
pos = match_SIFT(descriptor_source, descriptor_target)
H = affine_matrix(keypoint_source, keypoint_target, pos)
rows, cols, _ = img_target.shape
warp = cv2.warpAffine(img_source, H, (cols, rows))
merge = np.uint8(img_target * 0.5 + warp * 0.5)
cv2.imshow('img', merge)
cv2.waitKey(0)
cv2.destroyAllWindows()