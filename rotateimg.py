from skimage import io
from skimage.transform import rotate
img = io.imread('cat_1.jpg')
img_rot = rotate(img, 20)
io.imshow(img_rot)
io.show()