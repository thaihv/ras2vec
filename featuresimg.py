'''
Created on Apr 28, 2020

@author: thaih
'''
import cv2
import numpy as np
import matplotlib.pyplot as plt
from Sift_Operations import *

Image1 = cv2.imread('cat_1.jpg')
Image2 = cv2.imread('cat_2.jpg')
Image1_gray = cv2.cvtColor(Image1, cv2.COLOR_BGR2GRAY)
Image2_gray = cv2.cvtColor(Image2, cv2.COLOR_BGR2GRAY)
Image1_key_points, Image1_descriptors = extract_sift_features(Image1_gray)
Image2_key_points, Image2_descriptors = extract_sift_features(Image2_gray)
print( 'Displaying SIFT Features')
showing_sift_features(Image1_gray, Image1, Image1_key_points);
norm = cv2.NORM_L2
bruteForce = cv2.BFMatcher(norm)
matches = bruteForce.match(Image1_descriptors, Image2_descriptors)
matches = sorted(matches, key = lambda match:match.distance)
matched_img = cv2.drawMatches(
Image1, Image1_key_points,
Image2, Image2_key_points,
matches[:100], Image2.copy())
plt.figure(figsize=(100,300))
plt.imshow(matched_img)
plt.show()