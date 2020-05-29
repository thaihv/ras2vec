'''
Created on Apr 28, 2020

@author: thaih
'''
import cv2
import numpy as np
import matplotlib.pyplot as plt
def extract_sift_features(img):
    sift_initialize = cv2.xfeatures2d.SIFT_create()
    key_points, descriptors = sift_initialize.detectAndCompute(img, None)
    return key_points, descriptors
def showing_sift_features(img1, img2, key_points):
    return plt.imshow(cv2.drawKeypoints(img1, key_points,img2.copy()))