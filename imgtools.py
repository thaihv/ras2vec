import cv2
#Read image 1
img1 = cv2.imread('cat_1.jpg')
#Read image 2
img2 = cv2.imread('cat_2.jpg')
#Define alpha and beta
alpha = 0.30
beta = 0.70
#Blend images
final_image = cv2.addWeighted(img1, alpha, img2, beta, 0.0)
#Show image
cv2.imshow('blended two cats', final_image)
cv2.waitKey(0)
cv2.destroyAllWindows() 