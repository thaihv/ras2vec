'''
Created on Apr 29, 2020

@author: thaih
'''
import cv2

img1 = cv2.imread("multifaces.jpg")
gray_img = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
cv2.imshow("Original_grayscale_image",gray_img)
haar_face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_alt.xml')
faces = haar_face_cascade.detectMultiScale(gray_img, scaleFactor=1.1, minNeighbors=5)
print(faces)
for (x, y, w, h) in faces:
    cv2.rectangle(img1, (x, y), (x+w, y+h), (0, 255, 0), 2)
    
cv2.imshow("Final_detected_image",img1)
cv2.waitKey(0)