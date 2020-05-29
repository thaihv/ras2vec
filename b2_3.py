import numpy as np
from requests.utils import quote
from skimage.measure import find_contours, points_in_poly, approximate_polygon
from skimage import io
from skimage import draw
from skimage import color
import cv2

# Styled google maps url showing only the buildings
safeURL_Style = quote('feature:landscape.man_made|element:geometry.stroke|visibility:on|color:0xff0000|weight:1')
workingUrl = "http://maps.googleapis.com/maps/api/staticmap?center=21.0312246,105.7646925&zoom=18&format=png32&sensor=false&size=6000x6000&maptype=roadmap&style=visibility:off&style=" + safeURL_Style + "&key=AIzaSyDcBFbe71HaCJHzWEHiuhHfhPPY9URP2GU"
print(workingUrl)

mainBuilding = None
img = io.imread(workingUrl)
img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
cv2.imshow('Original', img)

img1 = cv2.imread("black.png")
img1 = cv2.cvtColor(img1, cv2.COLOR_BGR2RGB)
cv2.imshow('Black', img1)

img = cv2.subtract(img, img1)
cv2.imshow('Subtract', img)

if cv2.waitKey(0) & 0xFF == ord('q'): 
    cv2.destroyAllWindows() 