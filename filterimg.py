'''
Created on Apr 28, 2020

@author: thaih
'''
#import required packages
import cv2
import numpy as np
from pylab import *
from skimage import io
#Read images for different blurring purposes
image_Original = cv2.imread("cat_1.jpg")
image_MedianBlur = cv2.imread("cat_1.jpg")
image_GaussianBlur = cv2.imread("cat_1.jpg")
image_BilateralBlur = cv2.imread("cat_1.jpg")
#Blur images
image_MedianBlur=cv2.medianBlur(image_MedianBlur,3)
image_GaussianBlur=cv2.GaussianBlur(image_GaussianBlur,(9,9),10)
image_BilateralBlur=cv2.bilateralFilter(image_BilateralBlur,9,100,75)
#Show images
figure(0)
io.imshow(image_Original)
figure(1)
io.imshow(image_MedianBlur)
figure(2)
io.imshow(image_GaussianBlur)
figure(3)
io.imshow(image_BilateralBlur)
figure(2)
io.show()