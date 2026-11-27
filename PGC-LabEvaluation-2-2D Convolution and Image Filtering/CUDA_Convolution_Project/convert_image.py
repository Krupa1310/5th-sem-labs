from PIL import Image
import numpy as np

img = Image.open("images/input.png").convert("L")

pixels = np.array(img, dtype=np.uint8)

pixels.tofile("images/input.raw")

print("Image converted to raw binary successfully!")
print("Image dimensions:", pixels.shape)
print("Data type:", pixels.dtype)
print("File size:", pixels.nbytes, "bytes")
