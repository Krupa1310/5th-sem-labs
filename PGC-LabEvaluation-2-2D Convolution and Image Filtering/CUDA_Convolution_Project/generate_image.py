from PIL import Image
import numpy as np

width = 2048
height = 2048

y, x = np.mgrid[0:height, 0:width]

image = (
    127
    + 50 * np.sin(x / 35)
    + 40 * np.cos(y / 45)
    + 35 * np.sin((x + y) / 60)
)

image = np.clip(image, 0, 255).astype(np.uint8)

img = Image.fromarray(image, mode="L")
img.save("images/input.png")

print("Image generated successfully!")
print("Width:", img.width)
print("Height:", img.height)
print("Mode:", img.mode)
print("Total pixels:", img.width * img.height)
